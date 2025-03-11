# app/service/info_interpreter.py
import json
import time

from typing import Any
from fastapi import Depends, HTTPException
from loguru import logger
from google import genai
from google.genai import types
import asyncio
from datetime import datetime

from app.core.setting import Setting, get_setting
from app.schema.interpreter_schema import InterpretReq, InterpretResp
from app.service.news_manager import NewsManager


class InfoInterpreter:
    """Service for generating reports from news data using Gemini API."""

    def __init__(self, settings: Setting = Depends(get_setting)):
        self._settings = settings
        self._gemini_client = genai.Client(api_key=self._settings.gemini_api_key)
        self._system_prompt_path = (
            self._settings.project_root / "app" / "prompts" / "interpret.txt"
        )
        self._news_manager = NewsManager(settings=self._settings)

    def _load_system_prompt(self) -> str:
        with open(self._system_prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()
        return system_prompt

    async def generate_report(self, req: InterpretReq) -> InterpretResp:
        start_time = time.time()
        # retrieve news data from database via self._news_manager

        # Prepare the context for Gemini
        context_text = ""

        # Add metadata about the report
        current_date = datetime.now().strftime("%Y年%m月%d日")
        context_text += f"Report Date: {current_date}\n"
        context_text += f"Number of Articles: {len(filtered_items)}\n\n"

        # Add article information
        for i, item in enumerate(filtered_items, 1):
            context_text += f"Article {i}: {item.title}\n"
            context_text += f"ID: {item.id}\n"
            context_text += f"Source: {item.source}, Published: {item.gmt8time}\n"
            if item.summary:
                context_text += f"Summary: {item.summary}\n"
            if item.content:
                # Limit content length to avoid token limits
                content = item.content
                if len(content) > 2000:  # Truncate long content
                    content = content[:2000] + "..."
                context_text += f"Content: {content}\n"
            context_text += "\n---\n\n"

        # Add special instructions for the desired output format
        context_text += (
            "Additional Instructions: Please format the output exactly as follows:\n"
        )
        context_text += (
            "1. Begin with a title in the format: '🌐 AI 每日速递 |📅 人工智能期刊"
            + current_date
            + " | 汇总 | 最新人工智能动态 🚀(预计阅读时间:20~25分钟)：'\n"
        )
        context_text += "2. Include a section titled '📑 目录' with a list of all articles, each prefixed with a relevant emoji\n"
        context_text += "3. For each article, follow the exact format shown below:\n"
        context_text += (
            "   - Title with emoji (e.g., '💼 Luminance获得7500万美元融资')\n"
        )
        context_text += "   - Detailed summary (labeled '摘要:')\n"
        context_text += "   - Numbered key points (labeled '关键点:'), each key point should start with a relevant emoji\n"
        context_text += "4. The final output should look exactly like the example I've provided, with consistent formatting\n\n"
        context_text += "For example, if the article is about AI funding, the emoji could be 💰, if it's about a new technology, it could be 🤖, etc.\n"

        # Load system prompt and replace context placeholder
        system_prompt = self._load_system_prompt()
        if not system_prompt:
            raise HTTPException(status_code=500, detail="System prompt not found")

        prompt_with_context = system_prompt.replace("{{context}}", context_text)

        # Generate report using Gemini API
        response = await asyncio.to_thread(
            self._gemini_client.models.generate_content,
            model="gemini-2.0-flash",
            contents=prompt_with_context,
            config=types.GenerateContentConfig(max_output_tokens=4000, temperature=0.2),
        )

        report_text = response.text

        # Save the report to a file
        timestamp = int(time.time())
        report_filename = f"report_{timestamp}.md"
        report_path = self._settings.assets_dir / report_filename
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_text)

        # Extract sections
        sections = self._extract_sections(report_text)

        end_time = time.time()
        logger.info(
            f"Report generation completed in {end_time - start_time:.2f} seconds"
        )

        return InterpretResp(
            timestamp=int(time.time()),
            report_file=report_filename,
            title=sections.get("title", "AI News Report"),
            summary=sections.get("summary", ""),
            key_points=sections.get("key_points", []),
            full_report=report_text,
        )

    def _extract_sections(self, report_text: str) -> dict[str, Any]:
        """Extract title, summary, and key points from generated report."""
        sections = {"title": "", "summary": "", "key_points": []}

        try:
            # Extract the title from the first line
            lines = report_text.split("\n")
            if lines and "AI 每日速递" in lines[0]:
                sections["title"] = lines[0].strip()
            else:
                # Fallback title if the expected format isn't found
                current_date = datetime.now().strftime("%Y年%m月%d日")
                sections["title"] = f"🌐 AI 每日速递 | 人工智能期刊 {current_date}"

            # Look for the table of contents section
            toc_index = -1
            for i, line in enumerate(lines):
                if "📑 目录" in line:
                    toc_index = i
                    break

            # Extract the summary from lines after the table of contents until the first article
            if toc_index > 0:
                toc_content = []
                i = toc_index + 1
                while i < len(lines) and not (
                    lines[i].strip().startswith("1.") or "摘要:" in lines[i]
                ):
                    if lines[i].strip():
                        toc_content.append(lines[i].strip())
                    i += 1

                if toc_content:
                    sections["summary"] = " ".join(toc_content)

            # Extract key points which will be the article titles in the table of contents
            # Just look for lines with emojis at the beginning to capture the article titles
            for line in lines:
                if line.strip() and any(
                    emoji in line[:3]
                    for emoji in [
                        "🚀",
                        "💰",
                        "🤖",
                        "📱",
                        "💼",
                        "📊",
                        "🔍",
                        "🌐",
                        "💻",
                        "🎯",
                        "📈",
                    ]
                ):
                    if (
                        "摘要:" not in line
                        and "关键点:" not in line
                        and len(line.strip()) < 50
                    ):
                        sections["key_points"].append(line.strip())

        except Exception as e:
            logger.error(f"Error extracting sections from report: {e}")

        return sections
