# 🔍 Multi-Source Search API

**API tìm kiếm và tổng hợp thông tin từ nhiều nguồn trên Internet**

Tìm kiếm từ: **Google**, **Facebook**, **Twitter/X**, **Reddit**, **News**, **YouTube**, **TikTok**, và các trang **chính phủ** (.gov)

---

## 🚀 Chạy nhanh (Quick Start)

### Windows:
```cmd
start.bat
```

### PowerShell/Linux/Mac:
```bash
python start_api.py
```

Server sẽ chạy tại: **http://localhost:8000**

---

## 📦 Cài đặt lần đầu

```bash
# Cài dependencies
pip install fastapi uvicorn aiohttp beautifulsoup4 lxml python-dateutil

# Chạy server
python start_api.py
```

**Lưu ý**: Crawl4AI đã được cài sẵn trong project cha (trustme_crawl4ai)

---

## 📖 API Endpoints

### 1. **GET /** - Thông tin API
```bash
curl http://localhost:8000/
```

### 2. **GET /health** - Health check
```bash
curl http://localhost:8000/health
```

### 3. **POST /search** - Tìm kiếm đồng bộ

**Request:**
```json
{
  "query": "Python FastAPI tutorial",
  "max_results": 20,
  "include_sources": ["google", "news"],
  "languages": ["en"],
  "deep_crawl": false
}
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/search" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"query":"ChatGPT","max_results":15,"include_sources":["google","news"],"deep_crawl":true}'
```

**Response:**
```json
{
  "request_id": "search_abc123",
  "query": "Python FastAPI tutorial",
  "results": [
    {
      "title": "FastAPI Tutorial",
      "content": "Full page content...",
      "snippet": "Short description...",
      "author": "Author Name",
      "published_time": "2025-11-12T10:00:00Z",
      "url": "https://example.com/tutorial",
      "source": "google",
      "domain": "example.com",
      "url_trust": true,
      "trust_score": 85.0,
      "language": "en",
      "word_count": 1500,
      "crawled_at": "2025-11-12T10:00:00Z",
      "crawl_success": true
    }
  ],
  "stats": {
    "total_found": 20,
    "total_crawled": 18,
    "total_failed": 2,
    "by_source": {"google": 15, "news": 5},
    "trusted_sources": 12,
    "untrusted_sources": 8,
    "processing_time_seconds": 5.2
  },
  "status": "completed"
}
```

### 4. **POST /search/async** - Tìm kiếm bất đồng bộ (khuyến nghị cho queries lớn)

**Bước 1**: Bắt đầu search
```powershell
$response = Invoke-RestMethod -Uri "http://localhost:8000/search/async" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"query":"AI news 2025","max_results":100,"include_sources":["all"],"deep_crawl":true}'

$request_id = $response.request_id
Write-Host "Request ID: $request_id"
```

**Response:**
```json
{
  "request_id": "search_abc123",
  "status": "processing",
  "estimated_time_seconds": 120
}
```

**Bước 2**: Lấy kết quả
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/search/result/$request_id"
```

---

## 🎯 Tham số Request

| Tham số | Kiểu | Mặc định | Mô tả |
|---------|------|----------|-------|
| `query` | string | *bắt buộc* | Từ khóa tìm kiếm |
| `max_results` | int | 100 | Số lượng kết quả (10-500) |
| `include_sources` | array | `["all"]` | Nguồn tìm kiếm |
| `languages` | array | `["en","vi"]` | Ngôn ngữ |
| `deep_crawl` | bool | `true` | Crawl full content |
| `timeout` | int | 300 | Timeout (30-600s) |

### Các nguồn hỗ trợ (`include_sources`):

| Source | Mô tả | Trust Score |
|--------|-------|-------------|
| `"google"` | Google search | 50 |
| `"news"` | Google News | 85 |
| `"facebook"` | Facebook posts | 25 |
| `"twitter"` | Twitter/X tweets | 25 |
| `"reddit"` | Reddit discussions | 30 |
| `"youtube"` | YouTube videos | 40 |
| `"tiktok"` | TikTok videos | 20 |
| `"government"` | Trang .gov | 95 |
| `"all"` | Tất cả nguồn | - |

---

## 💡 Ví dụ sử dụng

### 1. Tìm kiếm nhanh (không crawl)
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/search" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"query":"Python tutorial","max_results":10,"include_sources":["google"],"deep_crawl":false}'
```

### 2. Tìm kiếm sâu với nhiều nguồn
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/search" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"query":"AI trong giáo dục","max_results":50,"include_sources":["google","news","youtube"],"languages":["vi"],"deep_crawl":true}'
```

### 3. Tìm kiếm Social Media
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/search" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"query":"iPhone 16 review","max_results":30,"include_sources":["twitter","facebook","reddit"],"deep_crawl":false}'
```

### 4. Chỉ nguồn tin cậy
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/search" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"query":"climate change policy","max_results":25,"include_sources":["news","government"],"deep_crawl":true}'
```

### 5. Async search (queries lớn)
```powershell
# Start search
$resp = Invoke-RestMethod -Uri "http://localhost:8000/search/async" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"query":"Quantum computing 2025","max_results":100,"include_sources":["all"],"deep_crawl":true}'

# Wait and get result
Start-Sleep -Seconds 30
Invoke-RestMethod -Uri "http://localhost:8000/search/result/$($resp.request_id)" | ConvertTo-Json -Depth 5
```

---

## 📊 Response Fields

### SearchResult Object

| Field | Type | Mô tả |
|-------|------|-------|
| `title` | string | Tiêu đề |
| `content` | string | Nội dung đầy đủ (nếu crawl thành công) |
| `snippet` | string | Đoạn trích ngắn |
| `author` | string | Tác giả (nếu có) |
| `published_time` | string | Thời gian publish (ISO 8601) |
| `url` | string | URL gốc |
| `source` | string | Nguồn (google, facebook, etc.) |
| `domain` | string | Domain name |
| `url_trust` | boolean | Nguồn tin cậy? |
| `trust_score` | float | Điểm tin cậy (0-100) |
| `language` | string | Ngôn ngữ |
| `word_count` | int | Số từ |
| `crawled_at` | string | Thời gian crawl |
| `crawl_success` | boolean | Crawl thành công? |
| `crawl_error` | string | Lỗi crawl (nếu có) |

### Stats Object

| Field | Type | Mô tả |
|-------|------|-------|
| `total_found` | int | Tổng số kết quả tìm được |
| `total_crawled` | int | Số kết quả crawl thành công |
| `total_failed` | int | Số kết quả crawl thất bại |
| `by_source` | object | Phân bố theo nguồn |
| `trusted_sources` | int | Số nguồn tin cậy |
| `untrusted_sources` | int | Số nguồn cần verify |
| `processing_time_seconds` | float | Thời gian xử lý |

---

## 🔒 Trust Assessment

### url_trust = true (Nguồn tin cậy):
- ✅ Trang chính phủ: `.gov`, `.gov.vn`, `chinhphu.vn`
- ✅ Báo chí lớn: `vnexpress.net`, `thanhnien.vn`, `tuoitre.vn`, `bbc.com`, `cnn.com`, `reuters.com`
- ✅ Trang học thuật: `.edu`, `.ac.uk`

### url_trust = false (Cần kiểm chứng):
- ⚠️ Social media: Facebook, Twitter, TikTok
- ⚠️ Blog cá nhân
- ⚠️ Forum, Reddit
- ⚠️ Nguồn không xác định

---

## 🎓 Use Cases

### Research Assistant
Tìm tất cả thông tin về một chủ đề:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/search" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"query":"Machine learning in healthcare","max_results":100,"include_sources":["google","news"],"deep_crawl":true}'
```

### News Aggregation
Thu thập tin tức từ nhiều nguồn:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/search" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"query":"Chính sách giáo dục 2025","max_results":50,"include_sources":["news","government"],"languages":["vi"],"deep_crawl":true}'
```

### Social Media Monitoring
Theo dõi phản ứng trên mạng xã hội:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/search" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"query":"ChatGPT 5","max_results":50,"include_sources":["twitter","facebook","reddit"],"deep_crawl":false}'
```

---

## 🌐 Swagger UI

Mở browser: **http://localhost:8000/docs**

Interactive API documentation với:
- ✅ Try out các endpoints trực tiếp
- ✅ Xem schema chi tiết
- ✅ Download OpenAPI spec

---

## 🐛 Troubleshooting

### Lỗi: "ModuleNotFoundError: No module named 'crawl4ai'"
```bash
# Đảm bảo bạn đang chạy từ thư mục fact_check_api
python start_api.py  # Script này tự động set Python path
```

### Lỗi: "Connection refused" khi test
```bash
# Kiểm tra server có đang chạy không
curl http://localhost:8000/health

# Nếu không, start lại server
python start_api.py
```

### Crawl chậm / Timeout
- Giảm `max_results`
- Set `deep_crawl=false` để chỉ lấy snippet
- Tăng `timeout`
- Sử dụng `/search/async` thay vì `/search`

### Không tìm được kết quả
- Thử query khác (tiếng Việt có dấu đầy đủ)
- Thử thêm nguồn: `"include_sources": ["all"]`
- Kiểm tra internet connection

### Kết quả không có content
- Enable `deep_crawl=true`
- Một số trang chặn crawler (Facebook, Twitter)
- Tăng timeout nếu trang load chậm

---

## 📁 Cấu trúc Project

```
fact_check_api/
├── models/
│   ├── __init__.py
│   └── simple_schemas.py      # Pydantic models
├── services/
│   ├── __init__.py
│   ├── enhanced_search.py     # Multi-source search
│   └── simple_crawler.py      # Crawl4AI crawler
├── simple_api.py              # Main FastAPI app
├── start_api.py               # Startup script
├── start.bat                  # Windows batch file
├── example_usage.py           # Python examples
├── requirements.txt           # Dependencies
├── .env.example               # Config template
└── README.md                  # This file
```

---

## ⚙️ Configuration

Tạo file `.env` (optional):

```bash
API_PORT=8000
API_HOST=0.0.0.0
MAX_CONCURRENT_CRAWLS=10
```

---

## 🔧 Development

### Run với auto-reload:
```bash
uvicorn simple_api:app --reload --host 0.0.0.0 --port 8000
```

### Test với Python script:
```bash
python example_usage.py
```

---

## 📝 API Response Status

| Status | Mô tả |
|--------|-------|
| `processing` | Đang xử lý (chỉ async) |
| `completed` | Hoàn thành |
| `failed` | Thất bại |

---

## 🎯 Best Practices

1. **Sử dụng async** cho queries lớn (>50 results) hoặc deep_crawl=true
2. **Giới hạn sources** nếu không cần tất cả (tăng tốc độ)
3. **Deep crawl** chỉ khi cần full content (chậm hơn)
4. **Kiểm tra trust_score** để filter nguồn tin cậy
5. **Handle timeout** với async và polling

---

## 📄 License

Apache 2.0

---

## 🤝 Support

- 📚 **Docs**: http://localhost:8000/docs
- 🐛 **Issues**: [GitHub Issues](https://github.com/minhduy6868/trustme_crawl4ai/issues)
- 💬 **Examples**: Xem `example_usage.py`

---

**Made with ❤️ using Crawl4AI**

🔗 **Crawl4AI**: https://github.com/unclecode/crawl4ai
