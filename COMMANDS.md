# 🚀 Quick Commands Reference

## Start Server

```bash
cd fact_check_api
python start_api.py
```

Or on Windows:
```cmd
cd fact_check_api
start.bat
```

**Server**: http://localhost:8000  
**Docs**: http://localhost:8000/docs

---

## PowerShell Test Commands

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

### Multi-Source Search
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/search" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"query":"AI news","max_results":30,"include_sources":["google","news","twitter","reddit"],"deep_crawl":false}'
```

### Deep Search (Full Content)
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/search" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"query":"ChatGPT","max_results":20,"include_sources":["google","news"],"deep_crawl":true}'
```

### Async Search (Large Queries)
```powershell
# Start search
$resp = Invoke-RestMethod -Uri "http://localhost:8000/search/async" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"query":"AI 2025","max_results":100,"include_sources":["all"],"deep_crawl":true}'

# Get result after some time
Start-Sleep -Seconds 20
Invoke-RestMethod -Uri "http://localhost:8000/search/result/$($resp.request_id)"
```

---

## All Sources Test
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/search" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"query":"technology news","max_results":50,"include_sources":["all"],"deep_crawl":false}'
```

---

## Documentation Links

- **Full Docs**: `fact_check_api/README.md`
- **Quick Start**: `fact_check_api/QUICKSTART.md`
- **Architecture**: `fact_check_api/STRUCTURE.md`
- **Test Results**: `TEST_RESULTS.md`
- **Examples**: Run `python fact_check_api/example_usage.py`
