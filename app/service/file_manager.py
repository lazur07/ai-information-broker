# app/service/file_manager.py
from pathlib import Path
import json
import os
from app.core import Setting, get_setting
from fastapi import HTTPException, Depends

from fastapi.responses import FileResponse
from loguru import logger

class FileManager:
    """Service for managing scraped news files."""
    
    def __init__(self, settings: Setting = Depends(get_setting)):
        self._settings = settings
        # Ensure assets directory exists
        self._settings.assets_dir.mkdir(parents=True, exist_ok=True)
    
    def list_files(self) -> list[dict]:
        """Returns a list of available JSON files in the assets directory with metadata."""
        results = []
        assets_dir = self._settings.assets_dir

        if not assets_dir.exists():
            return results

        for file_path in sorted(assets_dir.glob("*.json"), reverse=True):
            try:
                filename = file_path.name

                # Parse time range from filename (expected format: YYYYMMDDHHMMSS - YYYYMMDDHHMMSS.json)
                parts = filename.split(" - ")
                if len(parts) == 2 and parts[1].endswith(".json"):
                    time_range = f"{parts[0]} to {parts[1][:-5]}"
                else:
                    time_range = "Unknown time range"

                # Get article count by loading the JSON file
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    article_count = len(data)

                # Get file size
                file_size = os.path.getsize(file_path)
                file_size_kb = round(file_size / 1024, 1)

                results.append({
                    "filename": filename,
                    "time_range": time_range,
                    "article_count": article_count,
                    "file_size": f"{file_size_kb} KB",
                    "created": os.path.getctime(file_path),
                })
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
                # Skip files that can't be processed
                continue

        return results
    
    def get_file(self, filename: str) -> FileResponse:
        """Returns a file response for a specific JSON file."""
        file_path = self._settings.assets_dir / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File {filename} not found")

        return FileResponse(
            path=str(file_path), 
            filename=filename, 
            media_type="application/json"
        )