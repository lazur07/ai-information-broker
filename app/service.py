import requests, html, json, random, time, pytz, re
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial
from loguru import logger
from contextlib import contextmanager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, TimeoutException
from app.schema import InfoCollectReq, InfoCollectResp, NewsItem, NewsSource


class InfoScraper:
    """Service for scraping AI news from multiple sources."""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.china_tz = pytz.timezone("Asia/Shanghai")
        # Main driver used for navigation and network log extraction (used serially)
        self.driver = None  
        # Single executor for all blocking tasks
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.session = requests.Session()  # Reuse the HTTP session
        self.start_timestamp = None
        self.end_timestamp = None

    async def scrape(self, req: InfoCollectReq) -> InfoCollectResp:
        """Scrape news from multiple sources in parallel and return a consolidated response."""
        now = datetime.now()
        current_time = self._format_timestamp(int(now.timestamp()))
        self._calculate_time_range(req.days_back, now)
        logger.info(f"Starting scrape with parameters: {req.model_dump()} at {current_time}")

        # Launch scraping tasks for each source concurrently
        tasks = []
        for source_name in req.source:
            logger.info(f"Preparing to scrape from {source_name}")
            if source_name == NewsSource.TECHCRUNCH.value:
                tasks.append(self._run_in_executor(
                    partial(self._scrape_techcrunch, req.category, days_back=req.days_back)
                ))
            elif source_name == NewsSource.KR36.value:
                tasks.append(self._run_in_executor(self._scrape_36kr, req.category))

        results = await asyncio.gather(*tasks)
        all_news_items = [item for sublist in results for item in sublist]
        logger.info(f"Total articles before filtering: {len(all_news_items)}")

        filtered_items = self._filter_items(all_news_items, self.start_timestamp, self.end_timestamp, req.limit)
        logger.info(f"Returning {len(filtered_items)} filtered articles")
        return InfoCollectResp(timestamp=current_time, total_count=len(filtered_items), items=filtered_items)

    async def _run_in_executor(self, func, *args, **kwargs):
        """Run a blocking function in a thread pool executor."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self.executor, lambda: func(*args, **kwargs))

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
        """Calculate and store time range based on days_back using a base time."""
        self.end_timestamp = int(base_time.timestamp())
        self.start_timestamp = int((base_time - timedelta(days=days_back)).timestamp())
        logger.info(f"Time range: {datetime.fromtimestamp(self.start_timestamp)} to {datetime.fromtimestamp(self.end_timestamp)}")

    def _filter_items(self, items: list[NewsItem], start_time: int, end_time: int, limit: int) -> list[NewsItem]:
        logger.info(f"Filtering articles between {datetime.fromtimestamp(start_time)} and {datetime.fromtimestamp(end_time)}")
        filtered = [item for item in items if start_time <= item.publish_timestamp <= end_time]
        filtered.sort(key=lambda x: x.publish_timestamp, reverse=True)
        return filtered[:limit] if limit > 0 else filtered

    def _clean_text(self, html_text: str) -> str:
        if not html_text:
            return ""
        text = re.sub(r"<[^>]+>", " ", html_text)
        return re.sub(r"\s+", " ", html.unescape(text)).strip()

    def _format_timestamp(self, ts: int) -> str:
        return datetime.fromtimestamp(ts, self.china_tz).strftime("%Y-%m-%d %H:%M:%S")

    def _get_driver(self):
        """Get or create a Selenium WebDriver instance for serial tasks."""
        if self.driver is None:
            logger.info("Initializing main Chrome WebDriver")
            options = Options()
            if self.headless:
                options.add_argument("--headless=new")
                options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        return self.driver

    def _create_new_driver(self):
        """Create a new Selenium WebDriver instance for concurrent tasks."""
        logger.info("Creating new Chrome WebDriver instance for thread")
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
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
            "Accept": accept or "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        }
        if referer:
            headers["Referer"] = referer
        return headers

    # TechCrunch scraping methods
    def _scrape_techcrunch(self, category: str = "AI", days_back: int = 1) -> list[NewsItem]:
        logger.info(f"Scraping TechCrunch for category: {category} with days_back={days_back}")
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days_back)
        params = {
            "meta_key": "articleSection",
            "meta_value": category,
            "after": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "before": end_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "per_page": 30,
            "_embed": "wp:featuredmedia",
            "orderby": "date",
            "order": "desc",
        }
        base_url = "https://techcrunch.com/wp-json/wp/v2/posts"
        response = self.session.get(
            base_url,
            params=params,
            timeout=10,
            headers=self._get_headers(referer="https://techcrunch.com/", accept="application/json")
        )
        posts = response.json()
        logger.info(f"Found {len(posts)} TechCrunch articles")

        news_items = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self._create_techcrunch_item, post, i, len(posts))
                       for i, post in enumerate(posts)]
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
            gmt8_time = dt.astimezone(self.china_tz).strftime("%Y-%m-%d %H:%M:%S")
        else:
            publish_ts, gmt8_time = 0, ""
        # Enhanced logging: log each article with title and publish time
        logger.info(f"Processed TechCrunch article: '{title}' published at {gmt8_time}")
        return NewsItem(
            id=f"tc_{post.get('id', '')}",
            url=post.get("link", ""),
            title=title,
            author=str(post.get("author", "")),
            summary=self._clean_text(post.get("excerpt", {}).get("rendered", "")),
            content=self._clean_text(post.get("content", {}).get("rendered", "")),
            publish_timestamp=publish_ts,
            gmt8time=gmt8_time,
            source=NewsSource.TECHCRUNCH.value,
        )

    # 36kr scraping methods
    def _scrape_36kr(self, category: str = "AI") -> list[NewsItem]:
        logger.info(f"Scraping 36kr for category: {category}")
        
        with self.safe_driver() as driver:
            try:
                # Configure CDP for better network monitoring
                driver.execute_cdp_cmd('Network.enable', {})
                
                # Set up headers that mimic a real browser
                headers = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
                    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                    "Referer": "https://36kr.com/"
                }
                driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": headers})
                
                # Navigate with longer timeout and more careful scrolling
                logger.info(f"Navigating to: https://36kr.com/information/{category}/")
                driver.get(f"https://36kr.com/information/{category}/")
                time.sleep(10)  # Give page more time to fully load
                
                # Use more gradual scrolling to appear more human-like
                for i in range(3):
                    height = driver.execute_script("return document.body.scrollHeight")
                    for step in range(1, 6):  # Scroll in steps of 20%
                        scroll_to = height * step / 5
                        driver.execute_script(f"window.scrollTo(0, {scroll_to});")
                        time.sleep(1)
                    time.sleep(3)  # Wait between complete scrolls
                
                raw_articles = []
                self._process_36kr_network_logs(driver, raw_articles)
                logger.info(f"Found {len(raw_articles)} articles from 36kr network logs")
                
                # If no articles found through API, try direct scraping
                if not raw_articles:
                    logger.warning("No articles found via API, trying direct element scraping")
                    article_elements = driver.find_elements(By.CSS_SELECTOR, ".article-item")
                    
                    for idx, elem in enumerate(article_elements[:20]):  # Limit to first 20
                        try:
                            title_elem = elem.find_element(By.CSS_SELECTOR, ".article-item-title")
                            title = title_elem.text
                            url = title_elem.get_attribute("href") or ""
                            
                            # Extract other data as available
                            item_id = url.split("/")[-1] if url else f"manual_{idx}"
                            timestamp = int(time.time())  # Default to current time
                            
                            article = {
                                "id": f"kr36_{item_id}",
                                "url": url,
                                "title": title,
                                "source": NewsSource.KR36.value,
                                "author": "",
                                "summary": "",
                                "content": "",
                                "publish_timestamp": timestamp,
                                "gmt8time": self._format_timestamp(timestamp),
                            }
                            raw_articles.append(article)
                            logger.info(f"Manually extracted article: {title}")
                        except Exception as e:
                            logger.error(f"Error extracting article {idx}: {e}")
                
                # Process content only for filtered articles
                if raw_articles:
                    content_articles = sorted(
                        [a for a in raw_articles if self.start_timestamp <= a.get("publish_timestamp", 0) <= self.end_timestamp],
                        key=lambda x: x.get("publish_timestamp", 0),
                        reverse=True
                    )[:20]  # Limit to 20 articles
                    
                    # Use our existing executor rather than creating a new one
                    futures = {}
                    for article in content_articles:
                        futures[self.executor.submit(self._fetch_single_article_content, article)] = article
                    
                    for future in as_completed(futures):
                        try:
                            article = futures[future]
                            content = future.result()
                            if content:
                                article["content"] = content
                        except Exception as e:
                            logger.error(f"Error processing article content: {e}")
                
                news_items = [NewsItem(**article) for article in raw_articles]
                logger.info(f"36kr scraping complete: {len(news_items)} articles found")
                return news_items
                
            except Exception as e:
                logger.error(f"Error during 36kr scraping: {e}")
                return []  # Return empty list rather than crashing

    def _fetch_single_article_content(self, article):
        """Fetch content for a single 36kr article using a dedicated driver instance."""
        with self.safe_driver() as local_driver:
            try:
                local_driver.get(article["url"])
                time.sleep(8)  # Give page more time to load
                
                selectors = [
                    "#app > div > div.box-kr-article-new-y > div > div.kr-layout-main.clearfloat > div.main-right > div > div > div > div.article-detail-wrapper-box > div > div.article-left-container > div.article-content > div > div > div.common-width.margin-bottom-20 > div",
                    ".article-content",
                    ".article-detail",
                    ".kr-article-content",
                    ".common-width"
                ]
                
                content = ""
                for selector in selectors:
                    elements = local_driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        content = elements[0].text
                        if content and len(content) > 100:  # Only use if meaningful content found
                            logger.debug(f"Content found with selector '{selector}': {len(content)} chars")
                            break
                
                # If no content found, try to get any text from the page
                if not content:
                    body_elements = local_driver.find_elements(By.TAG_NAME, "body")
                    if body_elements:
                        content = body_elements[0].text
                        logger.warning(f"Used body fallback for {article['url']}, content length: {len(content)}")
                
                return content
            except Exception as e:
                logger.error(f"Error fetching content for article {article.get('url', 'unknown')}: {e}")
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
            if "gateway.36kr.com/api/mis/nav/ifm/subNav/flow" not in url or "json" not in response.get("mimeType", ""):
                continue
            request_id = log_data["params"]["requestId"]
            body_result = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
            if body_result and "body" in body_result:
                data = json.loads(body_result["body"])
                found_responses += 1
                if "data" in data:
                    items = data["data"].get("itemList", data["data"].get("itemlist", []))
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
            "content": "",
            "publish_timestamp": int(publish_ts),
            "gmt8time": gmt8_time,
        }
        articles.append(article)