# AI Information Broker

A microservice for automated scraping, filtering, and processing of AI-related news from global sources.

## Overview

AI Information Broker is a specialized web scraper designed to collect and process AI-related news from multiple sources (currently TechCrunch and 36kr). It automates the process of gathering articles, extracting content, and preparing the data for further processing or publishing.

## Features

- **Multi-source scraping**: Collects AI news from both Western (TechCrunch) and Chinese (36kr) sources
- **Time-based filtering**: Filters articles based on publication date
- **Parallel processing**: Uses asynchronous operations and thread pools for efficient scraping

## Installation

### Prerequisites

- Python 3.11
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

The API will be available at `http://localhost:8000`.

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
  "timestamp": "2025-03-05 20:45:59",
  "total_count": 20,
  "items": [
    {
      "id": "tc_12345",
      "url": "https://techcrunch.com/2025/03/05/example-article/",
      "title": "Example Article Title",
      "author": "John Doe",
      "summary": "This is an example summary...",
      "content": "Full article content...",
      "publish_timestamp": 1709665200,
      "gmt8time": "2025-03-05 05:00:00",
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
  "service": "ai-journalist"
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

### Data Processing Pipeline

1. Request received with time range and sources
2. Sources are scraped in parallel using async tasks
3. Articles are filtered based on publication date
4. Content is extracted for each article
5. Results are returned and saved as JSON

## Troubleshooting

### Common Issues

- **No articles from 36kr**: The website structure or API may have changed. Check the logs and update the selectors or API endpoints.
- **WebDriver errors**: Ensure Chrome and ChromeDriver are up to date and compatible.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.