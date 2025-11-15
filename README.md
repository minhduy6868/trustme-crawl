# 🔍 Multi-Source Search API

**API tìm kiếm và tổng hợp thông tin từ nhiều nguồn trên Internet**

Powered by [Crawl4AI](https://github.com/unclecode/crawl4ai)

---

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/minhduy6868/trustme_crawl4ai.git
cd trustme_crawl4ai
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run API
```bash
cd fact_check_api
python start_api.py
```

**Server**: http://localhost:8000  
**Docs**: http://localhost:8000/docs

---

## ✨ Features

- ✅ **8 nguồn tìm kiếm**: Google, Facebook, Twitter, Reddit, News, YouTube, TikTok, Government
- ✅ **Deep crawling**: Trích xuất full content từ mỗi URL
- ✅ **Trust scoring**: Đánh giá độ tin cậy nguồn (0-100)
- ✅ **Async processing**: Xử lý queries lớn không bị timeout
- ✅ **Multi-language**: Hỗ trợ tiếng Việt, English
- ✅ **RESTful API**: JSON response, dễ tích hợp

---

## 📖 Documentation

- **[API Documentation](fact_check_api/README.md)** - Complete guide
- **[Quick Start](fact_check_api/QUICKSTART.md)** - Test commands
- **[Architecture](fact_check_api/STRUCTURE.md)** - Technical details

---

## 🎯 API Endpoints

### POST /search - Synchronous Search
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Python FastAPI",
    "max_results": 20,
    "include_sources": ["google", "news"],
    "deep_crawl": true
  }'
```

### POST /search/async - Asynchronous Search
```bash
# Start search
curl -X POST http://localhost:8000/search/async \
  -H "Content-Type: application/json" \
  -d '{
    "query": "AI trends 2025",
    "max_results": 100,
    "include_sources": ["all"],
    "deep_crawl": true
  }'

# Get result
curl http://localhost:8000/search/result/{request_id}
```

---

## 📊 Response Example

```json
{
  "request_id": "search_abc123",
  "query": "Python FastAPI",
  "results": [
    {
      "title": "FastAPI - Modern Python Framework",
      "content": "FastAPI is a modern, fast web framework...",
      "url": "https://fastapi.tiangolo.com",
      "source": "google",
      "domain": "fastapi.tiangolo.com",
      "url_trust": true,
      "trust_score": 85.0,
      "author": "Sebastián Ramírez",
      "published_time": "2025-01-15T10:00:00Z",
      "language": "en",
      "word_count": 1500,
      "crawl_success": true
    }
  ],
  "stats": {
    "total_found": 20,
    "total_crawled": 18,
    "trusted_sources": 15,
    "processing_time_seconds": 5.2
  },
  "status": "completed"
}
```

---

## 🌐 Supported Sources

| Source | Description | Trust Score |
|--------|-------------|-------------|
| `google` | Google search | 50 |
| `news` | Google News | 85 |
| `facebook` | Facebook posts | 25 |
| `twitter` | Twitter/X tweets | 25 |
| `reddit` | Reddit discussions | 30 |
| `youtube` | YouTube videos | 40 |
| `tiktok` | TikTok videos | 20 |
| `government` | .gov sites | 95 |

---

## 🔒 Trust Assessment

**High Trust (url_trust = true)**
- ✅ Government sites (.gov, .gov.vn)
- ✅ Major news (VnExpress, BBC, Reuters, CNN)
- ✅ Academic (.edu, .ac.uk)

**Verify (url_trust = false)**
- ⚠️ Social media
- ⚠️ Personal blogs
- ⚠️ Forums

---

## 💡 Use Cases

### 1. Research Assistant
```python
{
  "query": "Machine learning in healthcare",
  "max_results": 100,
  "include_sources": ["google", "news"],
  "deep_crawl": true
}
```

### 2. News Aggregation
```python
{
  "query": "AI policy Vietnam 2025",
  "max_results": 50,
  "include_sources": ["news", "government"],
  "languages": ["vi"]
}
```

### 3. Social Media Monitoring
```python
{
  "query": "iPhone 16 review",
  "include_sources": ["twitter", "facebook", "reddit"],
  "deep_crawl": false
}
```

---

## 📁 Project Structure

```
trustme_crawl4ai/
├── crawl4ai/                 # Crawl4AI core library
├── fact_check_api/           # Search API application
│   ├── models/               # Pydantic schemas
│   ├── services/             # Search & crawler services
│   ├── simple_api.py         # FastAPI app
│   ├── start_api.py          # Startup script
│   └── README.md             # API documentation
├── requirements.txt          # Python dependencies
├── setup.py                  # Package setup
└── README.md                 # This file
```

---

## 🛠️ Development

### Run with auto-reload
```bash
cd fact_check_api
uvicorn simple_api:app --reload --host 0.0.0.0 --port 8000
```

### Run examples
```bash
cd fact_check_api
python example_usage.py
```

---

## 🐛 Troubleshooting

**ModuleNotFoundError: No module named 'crawl4ai'**
```bash
# Use start_api.py which auto-configures Python path
cd fact_check_api
python start_api.py
```

**Crawl slow/timeout**
- Reduce `max_results`
- Set `deep_crawl=false`
- Use `/search/async` endpoint
- Increase `timeout` parameter

**No results found**
- Try different keywords
- Set `"include_sources": ["all"]`
- Check internet connection

---

## 📦 Requirements

- Python 3.11+
- FastAPI
- Crawl4AI
- aiohttp
- BeautifulSoup4

See [requirements.txt](requirements.txt) for full list.

---

## 🔗 Links

- **Crawl4AI**: https://github.com/unclecode/crawl4ai
- **FastAPI**: https://fastapi.tiangolo.com
- **Documentation**: [fact_check_api/README.md](fact_check_api/README.md)

---

## 📄 License

Apache 2.0 - See [LICENSE](LICENSE)

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push and create a Pull Request

---

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/minhduy6868/trustme_crawl4ai/issues)
- 📚 **Docs**: http://localhost:8000/docs (when running)
- 💬 **Examples**: [fact_check_api/example_usage.py](fact_check_api/example_usage.py)

---

**Made with ❤️ using Crawl4AI**

Version: 1.0.0 | Last Updated: November 12, 2025
