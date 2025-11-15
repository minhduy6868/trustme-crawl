# TrustMe Crawler API

Multi-source web crawler for fact-checking system.

## Purpose

Crawls and aggregates content from multiple sources:
- Google Search
- Facebook, Twitter, Reddit
- News sites
- YouTube, TikTok
- Government sites (.gov)

## Features

- Async crawling with Crawl4AI
- Multi-source search via DuckDuckGo
- Content extraction and cleaning
- Basic trust scoring
- Concurrent request handling

## Installation

```bash
cd fact_check_api
pip install -r requirements.txt
```

## Run

```bash
python start_api.py
```

API runs on **http://localhost:8000**

## API Endpoints

### POST /search

Search and crawl content from multiple sources.

**Request:**
```json
{
  "query": "search keywords",
  "max_results": 30,
  "include_sources": ["google", "news", "government"],
  "languages": ["vi", "en"],
  "deep_crawl": true
}
```

**Response:**
```json
{
  "request_id": "search_abc123",
  "query": "search keywords",
  "results": [
    {
      "title": "Article title",
      "content": "Full content...",
      "url": "https://...",
      "domain": "example.com",
      "trust_score": 85.0,
      "url_trust": true,
      "crawl_success": true
    }
  ],
  "stats": {
    "total_found": 30,
    "total_crawled": 28,
    "trusted_sources": 20
  }
}
```

## Configuration

Default settings work out of the box. Optional customization:

```bash
export API_PORT=8000
export MAX_CONCURRENT_CRAWLS=10
```

## Usage

This API is designed to be called by the **TrustMe Model API**, not directly by end users.

Model API → Crawler API → Returns data

## Documentation

API docs: http://localhost:8000/docs

## License

Apache 2.0
