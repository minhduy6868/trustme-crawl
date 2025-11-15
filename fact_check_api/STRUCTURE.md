# 📁 Fact Check API - File Structure

```
fact_check_api/
│
├── 📄 README.md              # Tài liệu đầy đủ (API docs, examples, troubleshooting)
├── 📄 QUICKSTART.md          # Hướng dẫn nhanh (test commands, cheat sheet)
├── 📄 requirements.txt       # Python dependencies
├── 📄 .env.example           # Config template
├── 📄 .gitignore             # Git ignore rules
│
├── 🐍 simple_api.py          # Main FastAPI application
├── 🐍 start_api.py           # Startup script (auto setup Python path)
├── 🐍 example_usage.py       # Python usage examples
├── 💻 start.bat              # Windows quick start
├── 📄 __init__.py            # Package marker
│
├── 📁 models/
│   ├── __init__.py
│   └── simple_schemas.py     # Pydantic models (SearchRequest, SearchResult, SearchResponse)
│
└── 📁 services/
    ├── __init__.py
    ├── enhanced_search.py    # Multi-source search service (Google, Facebook, Twitter, etc.)
    └── simple_crawler.py     # Crawl4AI content crawler

```

---

## 🚀 Cách chạy

### Option 1: Windows batch file
```cmd
start.bat
```

### Option 2: Python script
```bash
python start_api.py
```

### Option 3: Direct uvicorn
```bash
# Set Python path first
$env:PYTHONPATH="D:\tool\trust_me\trustme_crawl4ai;$env:PYTHONPATH"
uvicorn simple_api:app --reload --host 0.0.0.0 --port 8000
```

---

## 📚 Tài liệu

- **README.md**: Full documentation
- **QUICKSTART.md**: Quick reference & test commands
- **Swagger UI**: http://localhost:8000/docs (when server running)
- **example_usage.py**: Python code examples

---

## 🔧 Files giải thích

### Core Files

**simple_api.py**
- Main FastAPI application
- Endpoints: `/`, `/health`, `/search`, `/search/async`, `/search/result/{id}`
- Trust scoring logic
- Background task processing

**start_api.py**
- Auto-configure Python path
- Check dependencies
- Start uvicorn server

**start.bat**
- Windows quick launcher
- Calls start_api.py

### Models

**models/simple_schemas.py**
- `SearchRequest`: Input model (query, max_results, include_sources, languages, deep_crawl, timeout)
- `SearchResult`: Single result (title, content, url, source, trust_score, etc.)
- `SearchResponse`: API response (results, stats, status)
- `SearchStats`: Statistics (total_found, by_source, processing_time)
- `SearchProgress`: Async search progress

### Services

**services/enhanced_search.py**
- `EnhancedSearchService`: Multi-source search
- Methods: `search_all()`, `_search_google()`, `_search_facebook()`, `_search_twitter()`, `_search_reddit()`, `_search_youtube()`, `_search_tiktok()`, `_search_government_sites()`
- DuckDuckGo HTML parsing
- Async context manager

**services/simple_crawler.py**
- `SimpleContentCrawler`: Crawl4AI wrapper
- Methods: `crawl_all()`, `_crawl_single()`
- Content extraction: title, author, publish_time, language
- Concurrent crawling with semaphore

### Config

**.env.example**
- Optional environment variables
- API_PORT, API_HOST, MAX_CONCURRENT_CRAWLS

**requirements.txt**
- FastAPI, uvicorn, aiohttp
- beautifulsoup4, lxml
- pydantic, python-dateutil
- Note: crawl4ai from parent project

---

## 🎯 Architecture

```
User Request
    ↓
FastAPI Endpoint (/search or /search/async)
    ↓
EnhancedSearchService
    ├→ DuckDuckGo Search (Google)
    ├→ DuckDuckGo Search (Facebook)
    ├→ DuckDuckGo Search (Twitter)
    ├→ DuckDuckGo Search (Reddit)
    ├→ DuckDuckGo Search (News)
    ├→ DuckDuckGo Search (YouTube)
    ├→ DuckDuckGo Search (TikTok)
    └→ DuckDuckGo Search (Government)
    ↓
List of URLs
    ↓
SimpleContentCrawler (if deep_crawl=true)
    ├→ Crawl4AI AsyncWebCrawler
    ├→ Extract full content
    ├→ Detect language
    ├→ Extract author
    └→ Extract publish time
    ↓
Trust Assessment
    ├→ Check domain (.gov, major news)
    ├→ Calculate trust_score
    └→ Set url_trust flag
    ↓
Response with results + stats
```

---

## 🔍 Key Components

### 1. Search Strategy
- Uses DuckDuckGo HTML search (no API key needed)
- Parallel searches across multiple sources
- Site-specific search queries (e.g., `site:facebook.com`)

### 2. Crawling Strategy
- Crawl4AI with Playwright browser
- Semaphore for concurrent control
- Markdown extraction
- Error handling per URL

### 3. Trust Scoring
- Government sites: 95 (high trust)
- Major news: 70-85 (trusted)
- Social media: 20-30 (verify)
- Unknown: 50 (neutral)

### 4. Async Processing
- Background tasks for large queries
- In-memory result storage
- Polling-based result retrieval

---

## 💡 Usage Patterns

### Pattern 1: Quick Research
```python
# Fast, many sources, no deep crawl
{"query": "topic", "max_results": 50, "include_sources": ["all"], "deep_crawl": false}
```

### Pattern 2: Deep Analysis
```python
# Slow, few sources, full content
{"query": "topic", "max_results": 20, "include_sources": ["news", "government"], "deep_crawl": true}
```

### Pattern 3: Social Monitoring
```python
# Fast, social media only
{"query": "topic", "include_sources": ["twitter", "facebook", "reddit"], "deep_crawl": false}
```

### Pattern 4: Large Dataset
```python
# Use async endpoint
POST /search/async {"query": "topic", "max_results": 200, "include_sources": ["all"], "deep_crawl": true}
GET /search/result/{request_id}
```

---

## 🛠️ Maintenance

### Add new source:
1. Add method in `enhanced_search.py` (e.g., `_search_instagram()`)
2. Add to `search_all()` source mapping
3. Update README docs

### Modify trust scoring:
1. Edit `_assess_url_trust()` in `simple_api.py`
2. Update trust_score values in `_calculate_trust_score()`

### Change crawler config:
1. Edit `BrowserConfig` in `simple_crawler.py`
2. Adjust timeout, headless, extra_args

---

## 📊 Current Limitations

1. **Crawl success rate**: Some sites block bots (Facebook, Twitter)
2. **Rate limiting**: No built-in rate limiting (add if needed)
3. **Caching**: In-memory only (consider Redis for production)
4. **Authentication**: No API auth (add if needed)
5. **Pagination**: No pagination support yet

---

## 🔜 Future Enhancements

- [ ] Add pagination for results
- [ ] Implement Redis caching
- [ ] Add API authentication (JWT)
- [ ] Real-time streaming (WebSocket)
- [ ] Export to CSV/JSON/PDF
- [ ] Duplicate detection
- [ ] Sentiment analysis
- [ ] More sources (Bing, Brave, Instagram)
- [ ] Advanced filtering & sorting
- [ ] Rate limiting middleware

---

**Last Updated**: November 12, 2025  
**Version**: 1.0.0  
**Status**: ✅ Production Ready
