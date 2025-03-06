# AI Information Broker


## Overview

AI Information Broker is a specialized web scraper designed to collect and process AI-related news from multiple sources (currently TechCrunch and 36kr). It automates the process of gathering articles, extracting content, and preparing the data for further processing or publishing.

## Features

- **Multi-source scraping**: Collects AI news from both Western (TechCrunch) and Chinese (36kr) sources
- **Time-based filtering**: Filters articles based on publication date
- **Parallel processing**: Uses asynchronous operations and thread pools for efficient scraping

## Installation

### Prerequisites

- Python 3.11 +
- Chrome browser
- ChromeDriver

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-information-broker.git
cd ai-information-broker
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your configuration (if needed)

## Usage

### Starting the Service

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. You can access the API documentation at `http://localhost:8000/data/docs`.

### API Endpoints

#### Scrape AI News

```
POST /data/info/scrape
```

Request body:
```json
{
  "days_back": 1,
  "category": "AI",
  "source": ["36kr", "techcrunch"],
  "limit": 20
}
```

Parameters:
- `days_back`: Number of days to look back for articles (default: 1)
- `category`: Category of articles to fetch (default: "AI")
- `source`: List of sources to scrape from (options: "techcrunch", "36kr")
- `limit`: Maximum number of articles to return

Response:
```json
{
  "timestamp": "2025-03-06 11:30:02",
  "total_count": 20,
  "items": [
    {
      "id": "tc_12345",
      "url": "https://techcrunch.com/2025/03/05/tapbots-teases-bluesky-app-phoenix/",
      "title": "Tapbots teases a new Bluesky app, Phoenix, saying it can't 'survive on Mastodon alone'",
      "author": "John Doe",
      "summary": "This is an example summary...",
      "content": "Full article content...",
      "publish_timestamp": 1709665200,
      "gmt8time": "2025-03-05 22:35:33",
      "source": "techcrunch"
    },
    // More items...
  ]
}
```

### Health Check

```
GET /
```

Returns:
```json
{
  "status": "running",
  "service": "ai-information-broker"
}
```

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── router.py        # API route definitions
│   ├── service.py       # Core scraping service
│   ├── schema.py        # Pydantic models
│   └── core.py          # Application settings and lifecycle
├── assets/              # Saved JSON data and test resources
├── logs/                # Application logs
├── .env                 # Environment variables
├── requirements.txt     # Project dependencies
└── README.md            # This file
```

## Implementation Details

### Scraping Methods

- **TechCrunch**: Uses the WordPress REST API to fetch articles directly
- **36kr**: Uses Selenium with Chrome DevTools Protocol (CDP) to intercept network requests and capture article data

### Safe Driver Management

The service uses a context manager to safely handle WebDriver instances:

```python
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
```


### Data Processing Pipeline

1. Request received with time range and sources
2. Sources are scraped in parallel using async tasks
3. Articles are filtered based on publication date
4. Content is extracted for each article with fallback selectors
5. Results are returned and saved to JSON files

## Troubleshooting

### Common Issues

- **No articles from 36kr**: The website structure or API may have changed. Check the logs and update the selectors or API endpoints.
- **WebDriver errors**: Ensure Chrome and ChromeDriver are up to date and compatible.
- **Rate limiting**: If you see 403 errors, try reducing scraping frequency or implementing a proxy rotation.

### Logs

Check the logs directory for detailed information about the scraping process:

```
logs/info.log    # General information and success messages
logs/error.log   # Error messages and exceptions
```

## Future Enhancements

Potential improvements for the project:

- Add a database to persist articles and avoid re-scraping the same content
- Implement content deduplication using similarity metrics 
- Add a translation service for Chinese content
- Create a simple frontend for browsing and selecting articles
- Implement a scheduled job to run the scraper at regular intervals

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
