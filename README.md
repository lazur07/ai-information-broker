# AI Information Broker


## Overview

AI Information Broker consists of two main components:
1. **Backend Service**: A specialized web scraper that collects AI news from multiple sources
2. **Frontend Application**: An iOS-inspired user interface for browsing and analyzing the collected news

## Features

- **Multi-source scraping**: Collects AI news from both Western (TechCrunch) and Chinese (36Kr) sources
- **Time-based filtering**: Filters articles based on publication date
- **Parallel processing**: Uses asynchronous operations for efficient scraping
- **File management**: Download articles in JSON format for offline analysis
- **Analytics dashboard**: Visualize data and gain insights from collected articles (coming soon)

## Backend Installation

### Prerequisites

- Python 3.11+
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

## Frontend Installation

### Prerequisites

- Node.js 16+ and npm/yarn
- Backend service running (for data access)

### Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. The frontend will be available at `http://localhost:5173`

## Usage

### Starting the Service

Start the FastAPI backend server:

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

#### List Available JSON Files

```
GET /data/info/files
```

Returns a list of available JSON files with metadata:
```json
[
  {
    "filename": "ai_news_20250305.json",
    "time_range": "20250301000000 to 20250305235959",
    "article_count": 42,
    "file_size": "156 KB",
    "created": 1709735461
  },
  {
    "filename": "ai_news_20250228.json",
    "time_range": "20250220000000 to 20250228235959",
    "article_count": 86,
    "file_size": "320 KB",
    "created": 1709304422
  }
]
```

#### Download a Specific JSON File

```
GET /data/info/files/{filename}
```

Returns the content of the specified JSON file.

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
├── app/                 # Backend application
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── router.py        # API route definitions
│   ├── service.py       # Core scraping service
│   ├── schema.py        # Pydantic models
│   └── core.py          # Application settings and lifecycle
├── frontend/            # Frontend application
│   ├── public/          # Static files
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── hooks/       # Custom React hooks
│   │   ├── types/       # TypeScript type definitions
│   │   ├── App.tsx      # Main application component
│   │   ├── index.css    # Global styles
│   │   └── main.tsx     # Application entry point
│   ├── index.html       # HTML template
│   ├── package.json     # Frontend dependencies
│   └── tailwind.config.js # TailwindCSS configuration
├── assets/              # Saved JSON data and test resources
├── logs/                # Application logs
├── .env                 # Environment variables
├── requirements.txt     # Backend dependencies
└── README.md            # This file
```

## Frontend Design

The frontend is built with a minimalist iOS-inspired design, featuring:

- **Fixed sidebar**: Easy access to filters and analytics from any section
- **Tabbed navigation**: Seamlessly switch between News, Files, and Analytics views
- **University of Toronto color scheme**: Primary blue (Pantone 655 - #1E3765) and Light blue (Pantone 2985 - #6FC7EA)
- **Responsive layout**: Optimized for both desktop and mobile devices
- **Smooth animations**: Subtle transitions for enhanced user experience

### UI Components

- **News Section**: Browse recent AI news with filtering options
- **Files Section**: Manage and download saved article collections
- **Analytics Section**: Visualize data and trends (placeholder for future development)

## Implementation Details

### Backend Scraping Methods

- **TechCrunch**: Uses the WordPress REST API to fetch articles directly
- **36kr**: Uses Selenium with Chrome DevTools Protocol (CDP) to intercept network requests and capture article data

### Frontend Technologies

- **React 18** with TypeScript for type safety
- **TailwindCSS** for styling with utility-first approach
- **Vite** for fast development and optimized builds

## Troubleshooting

### Common Backend Issues

- **No articles from 36kr**: The website structure or API may have changed. Check the logs and update the selectors or API endpoints.
- **WebDriver errors**: Ensure Chrome and ChromeDriver are up to date and compatible.
- **Rate limiting**: If you see 403 errors, try reducing scraping frequency or implementing a proxy rotation.

### Common Frontend Issues

- **API connection errors**: Ensure the backend server is running on the expected port
- **Styling issues**: Check browser compatibility for advanced CSS features
- **Component rendering problems**: Clear browser cache or check console for JavaScript errors

### Logs

Check the logs directory for detailed information about the scraping process:

```
logs/info.log    # General information and success messages
logs/error.log   # Error messages and exceptions
```

## Future Enhancements

Planned improvements for the project:

- **Backend**:
  - Add a database to persist articles and avoid re-scraping the same content
  - Implement content deduplication using similarity metrics
  - Add a translation service for Chinese content
  - Implement a scheduled job to run the scraper at regular intervals

- **Frontend**:
  - Add user authentication and personalization
  - Implement advanced analytics visualizations (word clouds, trend analysis, etc.)
  - Add article bookmarking and sharing features
  - Integrate a search function with filtering capabilities

## Building for Production

### Backend

For production deployment, consider using Gunicorn with Uvicorn workers:

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend

To create an optimized production build:

```bash
cd frontend
npm run build
```

The build output will be in the `dist` directory, ready to be deployed to a static hosting service.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.