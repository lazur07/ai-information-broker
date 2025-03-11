# app/service/info_scraper.py
import html
import json
import random
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from datetime import datetime, timedelta
from functools import partial
from pathlib import Path
from typing import List, Optional

import asyncio
import pytz
import requests
from fastapi import Depends
from loguru import logger
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from sqlmodel import Session, select
from webdriver_manager.chrome import ChromeDriverManager

from app.core.database import get_session
from app.core.setting import Setting, get_setting
from app.model.news_model import News, NewsSource
from app.schema.news_schema import NewsItem
from app.schema.scraper_schema import (ContentFetchReq, ContentFetchResp,
                                     ScrapeReq, ScrapeResp)


class InfoScraper:
    """Service for scraping AI news from multiple sources."""

    def __init__(
        self,
        headless: bool = True,
        settings: Setting = Depends(get_setting),
        db: Session = Depends(get_session),
    ):
        self._headless = headless
        self._settings = settings
        self._db = db
        self._china_tz = pytz.timezone("Asia/Shanghai")
        # Main driver used for navigation and network log extraction (used serially)
        self._driver = None
        # Single executor for all blocking tasks
        self._executor = ThreadPoolExecutor(max_workers=10)
        self._session = requests.Session()  # Reuse the HTTP session
        self._start_timestamp = None
        self._end_timestamp = None

    async def scrape(self, req: ScrapeReq) -> ScrapeResp:
        """Scrape news from multiple sources in parallel and return a consolidated response."""
        now = datetime.now()
        current_time = self._format_timestamp(int(now.timestamp()))
        self._calculate_time_range(req.days_back, now)
        logger.info(
            f"Starting scrape with parameters: {req.model_dump()} at {current_time}"
        )

        # Launch scraping tasks for each source concurrently
        tasks = []
        for source_name in req.source:
            logger.info(f"Preparing to scrape from {source_name}")
            if source_name == NewsSource.TECHCRUNCH.value:
                tasks.append(
                    self._run_in_executor(
                        partial(
                            self._scrape_techcrunch,
                            req.category,
                            days_back=req.days_back,
                        )
                    )
                )
            elif source_name == NewsSource.KR36.value:
                tasks.append(self._run_in_executor(self._scrape_36kr, req.category))

        results = await asyncio.gather(*tasks)
        all_news_items = [item for sublist in results for item in sublist]
        logger.info(f"Total articles before filtering: {len(all_news_items)}")

        # Filter and sort items
        filtered_items = self._filter_items(
            all_news_items, self._start_timestamp, self._end_timestamp, req.limit
        )
        logger.info(f"Found {len(filtered_items)} filtered articles")
        
        # Save items to database
        saved_items = await self._save_to_database(filtered_items)
        
        # Trigger content fetch for new items (non-blocking)
        # We don't await this to keep the response time fast
        asyncio.create_task(self._auto_fetch_content([item.id for item in saved_items]))
        
        return ScrapeResp(
            timestamp=current_time,
            total_count=len(saved_items),
            items=saved_items,
        )

    async def _auto_fetch_content(self, item_ids: list[str]):
        """Automatically fetch content for newly saved items (only for 36kr articles)."""
        if not item_ids:
            return
            
        # Filter to only get 36kr articles that need content fetching
        kr36_ids = []
        for item_id in item_ids:
            if item_id.startswith('kr36_'):
                kr36_ids.append(item_id)
                
        if not kr36_ids:
            return
            
        logger.info(f"Auto-fetching content for {len(kr36_ids)} 36kr articles")
        fetch_req = ContentFetchReq(item_ids=kr36_ids)
        await self.fetch_content(fetch_req)

    async def fetch_content(self, req: ContentFetchReq) -> ContentFetchResp:
        """Fetch detailed content for a list of news items (primarily for 36kr)."""
        logger.info(f"Fetching content for {len(req.item_ids)} news items")
        
        # Get news items from database that need content
        stmt = select(News).where(
            News.id.in_(req.item_ids),
            News.content == None
        )
        items_to_fetch = self._db.exec(stmt).all()
        
        logger.info(f"Found {len(items_to_fetch)} items needing content")
        
        if not items_to_fetch:
            return ContentFetchResp(
                timestamp=self._format_timestamp(int(datetime.now().timestamp())),
                total_count=0,
                items=[],
            )
        
        # Fetch content in parallel (primarily 36kr articles)
        tasks = []
        for news in items_to_fetch:
            if news.source == NewsSource.KR36.value:
                tasks.append(
                    self._run_in_executor(
                        self._fetch_single_article_content, {"url": news.url, "id": news.id}
                    )
                )
        
        contents = await asyncio.gather(*tasks)
        updated_items = []
        
        # Update database with fetched content
        for i, content in enumerate(contents):
            if content:
                news = items_to_fetch[i]
                news.content = content
                self._db.add(news)
                
                # Convert SQLModel to dict first, then to Pydantic model
                news_dict = {
                    "id": news.id,
                    "url": news.url,
                    "title": news.title,
                    "author": news.author,
                    "summary": news.summary,
                    "content": news.content,
                    "publish_timestamp": news.publish_timestamp,
                    "gmt8time": news.gmt8time,
                    "source": news.source,
                    "is_interpreted": news.is_interpreted
                }
                updated_items.append(NewsItem(**news_dict))
        
        # Commit all changes at once
        if updated_items:
            self._db.commit()
            logger.info(f"Updated content for {len(updated_items)} articles")
        
        return ContentFetchResp(
            timestamp=self._format_timestamp(int(datetime.now().timestamp())),
            total_count=len(updated_items),
            items=updated_items,
        )

    async def _save_to_database(self, items: list[NewsItem]) -> list[NewsItem]:
        """Save news items to database, skipping duplicates."""
        # Get all existing IDs in one query for efficiency
        existing_ids = {
            id_tuple[0] 
            for id_tuple in self._db.exec(select(News.id).where(News.id.in_([item.id for item in items])))
        }
        logger.info(f"Found {len(existing_ids)} existing articles in database")
        
        # Filter items to only new ones
        new_items = []
        saved_items = []
        
        for item in items:
            if item.id in existing_ids:
                # Item exists in DB, use it in response without modifying
                stmt = select(News).where(News.id == item.id)
                existing = self._db.exec(stmt).first()
                saved_items.append(NewsItem.model_validate(existing))
                continue
                
            # Convert to SQLModel and add to batch
            db_item = News(
                id=item.id,
                url=item.url,
                title=item.title,
                author=item.author,
                summary=item.summary,
                content=item.content,  # TechCrunch will have content, 36kr will be None
                publish_timestamp=item.publish_timestamp,
                gmt8time=item.gmt8time,
                source=item.source,
                is_interpreted=False
            )
            self._db.add(db_item)
            new_items.append(db_item)
            saved_items.append(item)
        
        # Commit all new items at once
        if new_items:
            self._db.commit()
            logger.info(f"Saved {len(new_items)} new articles to database")
        
        return saved_items

    async def _run_in_executor(self, func, *args, **kwargs):
        """Run a blocking function in a thread pool executor."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, lambda: func(*args, **kwargs))

    # Helper methods
    @contextmanager
    def safe_driver(self):
        """Context manager to safely handle WebDriver lifecycle."""
        driver = None
        try:
            driver = self._create_new_driver()
            yield driver
        finally:
            if driver:
                try:
                    driver.quit()
                    logger.debug("Driver successfully closed")
                except WebDriverException:
                    logger.warning("Driver already closed or failed to close")

    def _calculate_time_range(self, days_back: int, base_time: datetime):
        # Convert base_time to UTC for consistent calculations
        utc_base_time = base_time.astimezone(pytz.UTC)
        self._end_timestamp = int(utc_base_time.timestamp())
        self._start_timestamp = int((utc_base_time - timedelta(days=days_back)).timestamp())
        logger.info(
            f"Time range: {datetime.fromtimestamp(self._start_timestamp, pytz.UTC)} to {datetime.fromtimestamp(self._end_timestamp, pytz.UTC)} (UTC)"
        )

    def _filter_items(
        self, items: list[NewsItem], start_time: int, end_time: int, limit: int
    ) -> list[NewsItem]:
        logger.info(
            f"Filtering articles between {datetime.fromtimestamp(start_time)} and {datetime.fromtimestamp(end_time)}"
        )
        filtered = [
            item for item in items if start_time <= item.publish_timestamp <= end_time
        ]
        filtered.sort(key=lambda x: x.publish_timestamp, reverse=True)
        return filtered[:limit] if limit > 0 else filtered

    def _clean_text(self, html_text: str) -> str:
        if not html_text:
            return ""
        text = re.sub(r"<[^>]+>", " ", html_text)
        return re.sub(r"\s+", " ", html.unescape(text)).strip()

    def _format_timestamp(self, ts: int) -> str:
        return datetime.fromtimestamp(ts, self._china_tz).strftime("%Y-%m-%d %H:%M:%S")

    def _get_driver(self):
        """Get or create a Selenium WebDriver instance for serial tasks."""
        if self._driver is None:
            logger.info("Initializing main Chrome WebDriver")
            options = Options()
            if self._headless:
                options.add_argument("--headless=new")
                options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
            self._driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), options=options
            )
        return self._driver

    def _create_new_driver(self):
        """Create a new Selenium WebDriver instance for concurrent tasks."""
        logger.info("Creating new Chrome WebDriver instance for thread")
        options = Options()
        if self._headless:
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )
        return driver

    def _navigate_to_url(self, driver, url):
        logger.info(f"Navigating to: {url}")
        driver.get(url)
        time.sleep(random.uniform(5.0, 10.0))

    def _scroll_to_bottom(self, driver):
        logger.info("Scrolling to bottom of page")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(2.0, 5.0))

    def _get_headers(self, referer=None, accept=None):
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/15.0 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/92.0.4515.131 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
        ]
        headers = {
            "User-Agent": random.choice(user_agents),
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "DNT": "1",
            "Connection": "keep-alive",
            "Accept": accept
            or "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        }
        if referer:
            headers["Referer"] = referer
        return headers

    # TechCrunch scraping methods
    def _scrape_techcrunch(
        self, category: str = "AI", days_back: int = 1
    ) -> list[NewsItem]:
        logger.info(
            f"Scraping TechCrunch for category: {category} with days_back={days_back}"
        )
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days_back)
        params = {
            "meta_key": "articleSection",
            "meta_value": category,
            "after": start_time.astimezone(pytz.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "before": end_time.astimezone(pytz.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "per_page": 30,
            "_embed": "wp:featuredmedia",
            "orderby": "date",
            "order": "desc",
        }
        base_url = "https://techcrunch.com/wp-json/wp/v2/posts"
        response = self._session.get(
            base_url,
            params=params,
            timeout=10,
            headers=self._get_headers(
                referer="https://techcrunch.com/", accept="application/json"
            ),
        )
        posts = response.json()
        logger.info(f"Found {len(posts)} TechCrunch articles")

        news_items = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(self._create_techcrunch_item, post, i, len(posts))
                for i, post in enumerate(posts)
            ]
            for future in as_completed(futures):
                news_items.append(future.result())
        return news_items

    def _create_techcrunch_item(self, post: dict, index: int, total: int) -> NewsItem:
        title = self._clean_text(post.get("title", {}).get("rendered", ""))
        logger.info(f"Processing TechCrunch article [{index+1}/{total}]: {title}...")
        date_str = post.get("date_gmt", "")
        if date_str:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            publish_ts = int(dt.timestamp())
            gmt8_time = dt.astimezone(self._china_tz).strftime("%Y-%m-%d %H:%M:%S")
        else:
            publish_ts, gmt8_time = 0, ""
            
        # Get content from WordPress API response directly
        content = self._clean_text(post.get("content", {}).get("rendered", ""))
        
        # Enhanced logging: log each article with title and publish time
        logger.info(f"Processed TechCrunch article: '{title}' published at {gmt8_time}")
        return NewsItem(
            id=f"tc_{post.get('id', '')}",
            url=post.get("link", ""),
            title=title,
            author=str(post.get("author", "")),
            summary=self._clean_text(post.get("excerpt", {}).get("rendered", "")),
            content=content,  # Set content immediately from WordPress API
            publish_timestamp=publish_ts,
            gmt8time=gmt8_time,
            source=NewsSource.TECHCRUNCH.value,
            is_interpreted=False
        )
    
    # Remove the TechCrunch content fetching method since we now get content directly from the API

    # 36kr scraping methods
    def _scrape_36kr(self, category: str = "AI") -> list[NewsItem]:
        logger.info(f"Scraping 36kr for category: {category}")

        with self.safe_driver() as driver:
            try:
                # Configure CDP for better network monitoring
                driver.execute_cdp_cmd("Network.enable", {})

                # Set up headers that mimic a real browser
                headers = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
                    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                    "Referer": "https://36kr.com/",
                }
                driver.execute_cdp_cmd(
                    "Network.setExtraHTTPHeaders", {"headers": headers}
                )

                # Navigate with longer timeout
                logger.info(f"Navigating to: https://36kr.com/information/{category}/")
                driver.get(f"https://36kr.com/information/{category}/")
                time.sleep(12.7)  # Give page more time to fully load

                # First, scrape articles directly from the DOM that might not be captured in network logs
                dom_articles = []
                try:
                    # Find all article items in the feed
                    article_elements = driver.find_elements(By.CSS_SELECTOR, ".information-flow-item")
                    logger.info(f"Found {len(article_elements)} article elements via DOM")
                    
                    for idx, elem in enumerate(article_elements[:30]):  # Get the first 30 articles
                        try:
                            # Find the article title and link - notice they're nested in multiple elements
                            title_elem = elem.find_element(By.CSS_SELECTOR, ".article-item-title")
                            title = title_elem.text.strip()
                            url = title_elem.get_attribute("href")
                            
                            # 36kr uses relative URLs, so prepend the domain if needed
                            if url and url.startswith('/'):
                                url = f"https://36kr.com{url}"
                            
                            # Extract article ID from URL 
                            item_id = url.split("/")[-1] if url else f"manual_{idx}"
                            
                            # Get summary if available
                            try:
                                summary_elem = elem.find_element(By.CSS_SELECTOR, ".article-item-description")
                                summary = summary_elem.text.strip()
                            except:
                                summary = ""
                            
                            # Get author
                            try:
                                author_elem = elem.find_element(By.CSS_SELECTOR, ".kr-flow-bar-author")
                                author = author_elem.text.strip()
                            except:
                                author = ""
                            
                            # Parse time information - 36kr shows relative times like "16分钟前", "1小时前"
                            try:
                                time_elem = elem.find_element(By.CSS_SELECTOR, ".kr-flow-bar-time")
                                time_text = time_elem.text.strip()
                                
                                # Get current time in Beijing timezone
                                now = datetime.now(self._china_tz)
                                publish_time = now  # Default to current time
                                
                                if "分钟前" in time_text:
                                    minutes = int(re.search(r'(\d+)分钟前', time_text).group(1))
                                    publish_time = now - timedelta(minutes=minutes)
                                elif "小时前" in time_text:
                                    hours = int(re.search(r'(\d+)小时前', time_text).group(1))
                                    publish_time = now - timedelta(hours=hours)
                                elif "昨天" in time_text:
                                    publish_time = now - timedelta(days=1)
                                elif "天前" in time_text:
                                    days = int(re.search(r'(\d+)天前', time_text).group(1))
                                    publish_time = now - timedelta(days=days)
                                
                                publish_ts = int(publish_time.timestamp())
                                gmt8_time = publish_time.strftime("%Y-%m-%d %H:%M:%S")
                            except Exception as e:
                                logger.error(f"Error parsing time for article {idx}: {e}")
                                publish_ts = int(now.timestamp())
                                gmt8_time = now.strftime("%Y-%m-%d %H:%M:%S")
                                
                            article = {
                                "id": f"kr36_{item_id}",
                                "url": url,
                                "title": title,
                                "source": NewsSource.KR36.value,
                                "author": author,
                                "summary": summary,
                                "content": None,  # Content will be fetched separately
                                "publish_timestamp": publish_ts,
                                "gmt8time": gmt8_time,
                                "is_interpreted": False
                            }
                            dom_articles.append(article)
                            logger.info(f"DOM extracted article: '{title}' published at {gmt8_time}")
                        except Exception as e:
                            logger.error(f"Error extracting DOM article {idx}: {e}")
                except Exception as e:
                    logger.error(f"Error during DOM scraping: {e}")
                
                # Use more gradual scrolling to appear more human-like for API capture
                for i in range(2):
                    height = driver.execute_script("return document.body.scrollHeight")
                    for step in range(1, 6):  # Scroll in steps of 20%
                        scroll_to = height * step / 5
                        driver.execute_script(f"window.scrollTo(0, {scroll_to});")
                        time.sleep(1.7)
                    time.sleep(3.2)  # Wait between complete scrolls

                # Continue with the network log processing to get articles loaded via API
                api_articles = []
                self._process_36kr_network_logs(driver, api_articles)
                logger.info(f"Found {len(api_articles)} articles from 36kr network logs")

                # Combine articles from both sources and deduplicate by URL
                raw_articles = []
                seen_urls = set()
                
                # First add DOM articles (they're more likely to be recent)
                for article in dom_articles:
                    if article["url"] not in seen_urls and article["url"]:
                        seen_urls.add(article["url"])
                        raw_articles.append(article)
                
                # Then add API articles that weren't already captured
                for article in api_articles:
                    if article["url"] not in seen_urls and article["url"]:
                        seen_urls.add(article["url"])
                        raw_articles.append(article)
                        
                logger.info(f"Combined {len(raw_articles)} unique articles from DOM and API")

                news_items = [NewsItem(**article) for article in raw_articles]
                logger.info(f"36kr scraping complete: {len(news_items)} articles found")
                return news_items

            except Exception as e:
                logger.error(f"Error during 36kr scraping: {e}")
                return []  # Return empty list rather than crashing
            
    def _fetch_single_article_content(self, article):
        """Fetch content for a single 36kr article using a dedicated driver instance."""
        with self.safe_driver() as driver:
            driver.get(article["url"])
            time.sleep(random.uniform(8.0, 10.0))  # Give page time to load

            # Try multiple selectors in order of specificity
            selectors = [
                "#app > div > div.box-kr-article-new-y > div > div.kr-layout-main.clearfloat > div.main-right > div > div > div > div.article-detail-wrapper-box > div > div.article-left-container > div.article-content > div > div > div.common-width.margin-bottom-20 > div",
                ".article-content",
                ".article-detail",
                ".kr-article-content",
                ".common-width",
                "body"  # Fallback to body if nothing else works
            ]

            for selector in selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and elements[0].text and len(elements[0].text) > 100:
                    content_length = len(elements[0].text)
                    logger.info(f"Found content ({content_length} chars) for {article['id']}")
                    return elements[0].text
            
            logger.warning(f"No content found for {article['id']}")
            return ""

    def _process_36kr_network_logs(self, driver, articles):
        logs = driver.get_log("performance")
        found_responses = 0
        for entry in logs:
            if "message" not in entry:
                continue
            log_data = json.loads(entry["message"])["message"]
            if log_data["method"] != "Network.responseReceived":
                continue
            response = log_data["params"]["response"]
            url = response.get("url", "")
            if (
                "gateway.36kr.com/api/mis/nav/ifm/subNav/flow" not in url
                or "json" not in response.get("mimeType", "")
            ):
                continue
            request_id = log_data["params"]["requestId"]
            body_result = driver.execute_cdp_cmd(
                "Network.getResponseBody", {"requestId": request_id}
            )
            if body_result and "body" in body_result:
                data = json.loads(body_result["body"])
                found_responses += 1
                if "data" in data:
                    items = data["data"].get(
                        "itemList", data["data"].get("itemlist", [])
                    )
                    logger.info(f"Processing {len(items)} items from 36kr API response")
                    for item in [i for i in items if "templateMaterial" in i]:
                        self._process_36kr_item(item, articles)
        logger.info(f"Processed {found_responses} API responses from 36kr")

    def _process_36kr_item(self, item, articles):
        material = item["templateMaterial"]
        item_id = str(item.get("itemId", ""))
        publish_ts = material.get("publishTime", 0)
        if publish_ts > 9999999999:
            publish_ts = publish_ts / 1000
        gmt8_time = self._format_timestamp(publish_ts)
        title = material.get("widgetTitle", "")
        # Enhanced logging: log each processed 36kr article
        logger.info(f"Processed 36kr article: '{title}' published at {gmt8_time}")
        article = {
            "id": f"kr36_{item_id}",
            "url": f"https://36kr.com/p/{item_id}",
            "title": title,
            "source": NewsSource.KR36.value,
            "author": material.get("authorName", ""),
            "summary": material.get("summary", ""),
            "content": None,  # Content will be fetched separately
            "publish_timestamp": int(publish_ts),
            "gmt8time": gmt8_time,
            "is_interpreted": False
        }
        articles.append(article)