# TrustMe Crawl - Fact Check API

**Multi-source web crawler and article analyzer for fact-checking system.**

## 🎯 Project Structure

```
trustme-crawl/
├── README.md                 # This documentation
├── crawl4ai/                 # Core crawler engine
├── fact_check_api/           # Article Analyze API
│   ├── api_server.py         # FastAPI application
│   ├── start_server.bat      # Windows startup script
│   ├── requirements.txt      # API dependencies
│   ├── .gitignore            # Git ignore patterns
│   ├── models/               # Pydantic schemas
│   │   ├── __init__.py
│   │   └── fact_check_schemas.py
│   └── services/             # Business logic
│       ├── __init__.py
│       ├── fact_check_service.py
│       ├── enhanced_search.py
│       └── simple_crawler.py
├── LICENSE
├── pyproject.toml
├── setup.py
└── requirements.txt          # Main project dependencies
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r fact_check_api/requirements.txt
```

### 2. Run API Server

**Windows:**
```bash
cd fact_check_api
start_server.bat
```

**Linux/Mac:**
```bash
cd fact_check_api
python api_server.py
```

Server runs on: **http://localhost:8001**

### 3. Test API

```bash
curl -X POST http://localhost:8001/api/article/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article",
    "article": "Your article content here...",
    "platform": "web"
  }'
```

## 📚 API Documentation

### Endpoint: **POST /api/article/analyze**

Analyze an article and find related content from multiple sources.

**Request Body:**
```json
{
  "url": "https://example.com/article",
  "title": "Article Title (optional)",
  "article": "Full article content",
  "created_at": "2024-11-23T10:00:00.000Z (optional)",
  "author": "Author name (optional)",
  "platform": "web",
  "image_urls": []
}
```

**Response:**
```json
{
  "main_search": {
    "url": "https://example.com/article",
    "title": "Article Title",
    "article": "Full article content",
    "platform": "web",
    "created_at": "2024-11-23T10:00:00.000Z",
    "author": "Author name",
    "image_urls": []
  },
  "data": [
    {
      "url": "https://related-article-1.com",
      "title": "Related Article Title",
      "article": "Clean text content (HTML removed)",
      "domain": "related-article-1.com",
      "created_at": null,
      "author": null,
      "platform": "web",
      "crawl_success": true,
      "image_urls": []
    }
  ],
  "meta": {
    "page": 1,
    "limit": 10,
    "total": 45,
    "has_next": false
  }
}
```

### Platform Values

- `web` - Website/Blog
- `facebook` - Facebook post
- `twitter` - Twitter/X post
- `youtube` - YouTube video
- `tiktok` - TikTok video
- `reddit` - Reddit post

## 🛠️ Technology Stack

- **FastAPI** - Modern async web framework
- **Crawl4AI** - Web crawler engine
- **BeautifulSoup4** - HTML parsing
- **aiohttp** - Async HTTP client
- **Pydantic v2** - Data validation

## 💡 API Examples

### 1. Health Check
```bash
curl http://localhost:8001/health
```

### 2. Analyze Vietnamese Article
```bash
curl -X POST http://localhost:8001/api/article/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://vnexpress.net/vaccine-covid-19",
    "title": "Vaccine COVID-19 thế hệ mới",
    "article": "Bộ Y tế Việt Nam vừa công bố phê duyệt vaccine COVID-19 thế hệ mới...",
    "platform": "web",
    "author": "VnExpress"
  }'
```

### 3. Analyze English Tech News
```bash
curl -X POST http://localhost:8001/api/article/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://techcrunch.com/ai-news",
    "title": "OpenAI Releases GPT-5",
    "article": "OpenAI announced today the release of GPT-5...",
    "platform": "web"
  }'
```

### 4. Analyze Facebook Post
```bash
curl -X POST http://localhost:8001/api/article/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://facebook.com/user/posts/123",
    "article": "Breaking news about new technology...",
    "platform": "facebook",
    "created_at": "2024-11-23T10:00:00.000Z"
  }'
```

### 5. Minimal Request
```bash
curl -X POST http://localhost:8001/api/article/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article",
    "article": "Article content here",
    "platform": "web"
  }'
```

**📚 More Documentation:**
- **Swagger UI**: http://localhost:8001/docs (interactive API docs)
- **ReDoc**: http://localhost:8001/redoc (alternative docs)

## 🔧 Configuration

Default settings:
- **Port**: 8001
- **Search sources**: Google + News
- **Max results**: 100 per query
- **Deep crawl**: Always enabled
- **Languages**: Auto-detect (Vietnamese + English)

## 🤝 Contributing

This is a private project for TrustMe fact-checking system.

## 📄 License

See LICENSE file for details.

---

**Built with ❤️ for TrustMe Fact-Checking System**
