# 🚀 Quick Start Guide

## Chạy Server

### Windows:
```cmd
start.bat
```

### PowerShell/Mac/Linux:
```bash
python start_api.py
```

**Server**: http://localhost:8000  
**Docs**: http://localhost:8000/docs

---

## Test Commands

### Health Check
```powershell
curl http://localhost:8000/health
```

### Quick Search (Fast)
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/search" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"query":"Python","max_results":10,"include_sources":["google"],"deep_crawl":false}'
```

### Deep Search (Full Content)
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/search" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"query":"AI news","max_results":20,"include_sources":["google","news"],"deep_crawl":true}'
```

### Multi-Source Search
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/search" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"query":"ChatGPT","max_results":30,"include_sources":["google","twitter","reddit","news"],"deep_crawl":false}'
```

### Async Search (Large Queries)
```powershell
# Start
$resp = Invoke-RestMethod -Uri "http://localhost:8000/search/async" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"query":"AI 2025","max_results":100,"include_sources":["all"],"deep_crawl":true}'

# Get result
Start-Sleep -Seconds 20
Invoke-RestMethod -Uri "http://localhost:8000/search/result/$($resp.request_id)"
```

---

## Available Sources

| Source | Description | Trust Score |
|--------|-------------|-------------|
| `google` | Google search | 50 |
| `news` | Google News | 85 |
| `facebook` | Facebook posts | 25 |
| `twitter` | Twitter/X | 25 |
| `reddit` | Reddit | 30 |
| `youtube` | YouTube | 40 |
| `tiktok` | TikTok | 20 |
| `government` | .gov sites | 95 |
| `all` | All sources | - |

---

## Key Parameters

```json
{
  "query": "search term",           // Required
  "max_results": 50,                // 10-500, default: 100
  "include_sources": ["google"],    // Default: ["all"]
  "languages": ["vi", "en"],        // Default: ["en", "vi"]
  "deep_crawl": true,               // Default: true (slow but full content)
  "timeout": 300                    // 30-600 seconds
}
```

---

## Response Format

```json
{
  "request_id": "search_abc123",
  "query": "Python",
  "results": [
    {
      "title": "Python.org",
      "content": "Full content...",
      "url": "https://python.org",
      "source": "google",
      "url_trust": true,
      "trust_score": 85.0,
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

## Troubleshooting

**Server won't start?**
```bash
python start_api.py
```

**Crawl failed?**
- Set `"deep_crawl": false`
- Reduce `max_results`
- Use async endpoint for large queries

**No results?**
- Try different query
- Set `"include_sources": ["all"]`
- Check internet connection

---

📚 **Full Docs**: See `README.md`  
🌐 **Swagger UI**: http://localhost:8000/docs  
💡 **Examples**: Run `python example_usage.py`
