"""
Simple Search API
API tìm kiếm và tổng hợp thông tin từ nhiều nguồn trên Internet
"""

import asyncio
import uuid
from datetime import datetime
from typing import Optional
import os
import time

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from models.simple_schemas import (
    SearchRequest,
    SearchResponse,
    SearchResult,
    SearchStats,
    SearchProgress,
)
from services.enhanced_search import EnhancedSearchService
from services.simple_crawler import SimpleContentCrawler


# Initialize FastAPI
app = FastAPI(
    title="Multi-Source Search API",
    description="API tìm kiếm và crawl thông tin từ Google, Facebook, Twitter, Reddit, News, v.v.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Services
crawler_service: Optional[SimpleContentCrawler] = None

# In-memory storage for async results
search_results_storage = {}


@app.on_event("startup")
async def startup_event():
    """Initialize services"""
    global crawler_service
    
    crawler_service = SimpleContentCrawler(max_concurrent=10)
    
    print("✅ Multi-Source Search API initialized")
    print("📡 Ready to search: Google, Facebook, Twitter, Reddit, News, YouTube, TikTok")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Multi-Source Search API",
        "version": "1.0.0",
        "description": "Tìm kiếm và crawl thông tin từ nhiều nguồn trên Internet",
        "status": "operational",
        "sources": [
            "Google",
            "Facebook", 
            "Twitter/X",
            "Reddit",
            "News Sites",
            "YouTube",
            "TikTok",
            "Government (.gov)",
        ],
        "endpoints": {
            "search": "POST /search - Tìm kiếm đồng bộ",
            "search_async": "POST /search/async - Tìm kiếm bất đồng bộ",
            "get_result": "GET /search/result/{request_id} - Lấy kết quả",
            "health": "GET /health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "crawler": crawler_service is not None,
        }
    }


@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Tìm kiếm đồng bộ - Trả về kết quả đầy đủ
    
    ⚠️ Có thể mất 30-300s tùy thuộc vào max_results và deep_crawl
    
    Để tránh timeout, khuyến nghị dùng /search/async
    """
    request_id = f"search_{uuid.uuid4().hex[:12]}"
    start_time = time.time()
    
    try:
        # Step 1: Search từ các nguồn
        async with EnhancedSearchService() as search_service:
            search_results = await search_service.search_all(
                query=request.query,
                max_results=request.max_results,
                include_sources=request.include_sources,
                languages=request.languages,
            )
        
        print(f"✅ Found {len(search_results)} results from search")
        
        # Step 2: Crawl content (nếu deep_crawl)
        if request.deep_crawl and search_results:
            crawled_results = await crawler_service.crawl_all(search_results)
            print(f"✅ Crawled {len([r for r in crawled_results if r.get('crawl_success')])} URLs")
        else:
            crawled_results = search_results
            # Mark as not crawled
            for result in crawled_results:
                result['crawl_success'] = False
                result['content'] = None
        
        # Step 3: Convert to SearchResult models and assess trust
        final_results = []
        by_source_count = {}
        trusted_count = 0
        untrusted_count = 0
        
        for result in crawled_results:
            # Assess trust
            domain = result.get('domain', '')
            source = result.get('source', 'google')
            url_trust = _assess_url_trust(domain, source)
            trust_score = _calculate_trust_score(domain, source)
            
            # Count by source
            by_source_count[source] = by_source_count.get(source, 0) + 1
            
            # Count trusted
            if url_trust:
                trusted_count += 1
            else:
                untrusted_count += 1
            
            # Create SearchResult
            search_result = SearchResult(
                title=result.get('title', 'No title'),
                content=result.get('content'),
                snippet=result.get('snippet'),
                author=result.get('author'),
                published_time=result.get('published_time'),
                url=result.get('url', ''),
                source=source,
                domain=domain,
                url_trust=url_trust,
                trust_score=trust_score,
                language=result.get('language'),
                word_count=result.get('word_count'),
                crawled_at=datetime.fromisoformat(result['crawled_at']) if result.get('crawled_at') else datetime.utcnow(),
                crawl_success=result.get('crawl_success', False),
                crawl_error=result.get('crawl_error'),
            )
            
            final_results.append(search_result)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Create response
        response = SearchResponse(
            request_id=request_id,
            query=request.query,
            results=final_results,
            stats=SearchStats(
                total_found=len(search_results),
                total_crawled=len([r for r in crawled_results if r.get('crawl_success')]),
                total_failed=len([r for r in crawled_results if not r.get('crawl_success')]),
                by_source=by_source_count,
                trusted_sources=trusted_count,
                untrusted_sources=untrusted_count,
                processing_time_seconds=processing_time,
            ),
            status="completed",
            completed_at=datetime.utcnow(),
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.post("/search/async")
async def search_async(request: SearchRequest, background_tasks: BackgroundTasks):
    """
    Tìm kiếm bất đồng bộ - Trả về request_id ngay lập tức
    
    Sử dụng GET /search/result/{request_id} để lấy kết quả
    """
    request_id = f"search_{uuid.uuid4().hex[:12]}"
    
    # Store initial status
    search_results_storage[request_id] = {
        "request_id": request_id,
        "query": request.query,
        "status": "processing",
        "created_at": datetime.utcnow().isoformat(),
    }
    
    # Start background task
    background_tasks.add_task(
        _process_search_background,
        request_id,
        request,
    )
    
    return {
        "request_id": request_id,
        "status": "processing",
        "message": "Search started. Sử dụng GET /search/result/{request_id} để lấy kết quả.",
        "estimated_time_seconds": request.max_results * 1.5,
    }


@app.get("/search/result/{request_id}")
async def get_search_result(request_id: str):
    """Lấy kết quả search theo request_id"""
    if request_id not in search_results_storage:
        raise HTTPException(status_code=404, detail="Request ID không tồn tại")
    
    return search_results_storage[request_id]


@app.delete("/search/result/{request_id}")
async def delete_search_result(request_id: str):
    """Xóa kết quả search khỏi bộ nhớ"""
    if request_id not in search_results_storage:
        raise HTTPException(status_code=404, detail="Request ID không tồn tại")
    
    del search_results_storage[request_id]
    return {"message": "Đã xóa kết quả"}


# ==================== Background Processing ====================

async def _process_search_background(request_id: str, request: SearchRequest):
    """Background task cho search"""
    start_time = time.time()
    
    try:
        # Search
        async with EnhancedSearchService() as search_service:
            search_results = await search_service.search_all(
                query=request.query,
                max_results=request.max_results,
                include_sources=request.include_sources,
                languages=request.languages,
            )
        
        # Crawl
        if request.deep_crawl and search_results:
            crawled_results = await crawler_service.crawl_all(search_results)
        else:
            crawled_results = search_results
            for result in crawled_results:
                result['crawl_success'] = False
                result['content'] = None
        
        # Process results
        final_results = []
        by_source_count = {}
        trusted_count = 0
        untrusted_count = 0
        
        for result in crawled_results:
            domain = result.get('domain', '')
            source = result.get('source', 'google')
            url_trust = _assess_url_trust(domain, source)
            trust_score = _calculate_trust_score(domain, source)
            
            by_source_count[source] = by_source_count.get(source, 0) + 1
            
            if url_trust:
                trusted_count += 1
            else:
                untrusted_count += 1
            
            search_result = SearchResult(
                title=result.get('title', 'No title'),
                content=result.get('content'),
                snippet=result.get('snippet'),
                author=result.get('author'),
                published_time=result.get('published_time'),
                url=result.get('url', ''),
                source=source,
                domain=domain,
                url_trust=url_trust,
                trust_score=trust_score,
                language=result.get('language'),
                word_count=result.get('word_count'),
                crawled_at=datetime.fromisoformat(result['crawled_at']) if result.get('crawled_at') else datetime.utcnow(),
                crawl_success=result.get('crawl_success', False),
                crawl_error=result.get('crawl_error'),
            )
            
            final_results.append(search_result)
        
        processing_time = time.time() - start_time
        
        # Store result
        response = SearchResponse(
            request_id=request_id,
            query=request.query,
            results=final_results,
            stats=SearchStats(
                total_found=len(search_results),
                total_crawled=len([r for r in crawled_results if r.get('crawl_success')]),
                total_failed=len([r for r in crawled_results if not r.get('crawl_success')]),
                by_source=by_source_count,
                trusted_sources=trusted_count,
                untrusted_sources=untrusted_count,
                processing_time_seconds=processing_time,
            ),
            status="completed",
            completed_at=datetime.utcnow(),
        )
        
        search_results_storage[request_id] = response.model_dump()
        
    except Exception as e:
        search_results_storage[request_id] = {
            "request_id": request_id,
            "query": request.query,
            "status": "failed",
            "error_message": str(e),
            "created_at": search_results_storage[request_id]["created_at"],
            "completed_at": datetime.utcnow().isoformat(),
        }


# ==================== Helper Functions ====================

def _assess_url_trust(domain: str, source: str) -> bool:
    """Đánh giá xem URL có đáng tin cậy không"""
    
    # Government domains = trusted
    gov_domains = [
        'gov.vn', 'gov', 'chinhphu.vn', 'baochinhphu.vn',
        'gov.uk', 'gov.au', 'gov.sg', 'europa.eu',
    ]
    
    if any(gov in domain for gov in gov_domains):
        return True
    
    # Major news outlets = trusted
    major_news = [
        'vnexpress.net', 'vietnamnet.vn', 'tuoitre.vn', 'thanhnien.vn',
        'dantri.com.vn', 'vtv.vn', 'vov.vn', 'nhandan.vn',
        'reuters.com', 'apnews.com', 'bbc.com', 'cnn.com',
    ]
    
    if any(news in domain for news in major_news):
        return True
    
    # Social media = not trusted for fact-checking
    social_media = ['facebook.com', 'twitter.com', 'x.com', 'tiktok.com', 'reddit.com']
    if any(social in domain for social in social_media):
        return False
    
    # Academic = trusted
    if '.edu' in domain or '.ac.' in domain:
        return True
    
    # Default: not trusted
    return False


def _calculate_trust_score(domain: str, source: str) -> float:
    """Tính trust score 0-100"""
    
    if _assess_url_trust(domain, source):
        # Trusted sources
        if 'gov' in domain:
            return 95.0
        elif any(news in domain for news in ['vnexpress', 'reuters', 'bbc']):
            return 85.0
        else:
            return 70.0
    else:
        # Untrusted sources
        social_media = ['facebook.com', 'twitter.com', 'x.com', 'tiktok.com']
        if any(social in domain for social in social_media):
            return 25.0
        elif 'blog' in domain:
            return 35.0
        else:
            return 50.0


# ==================== Run Server ====================

if __name__ == "__main__":
    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run(
        "simple_api:app",
        host="0.0.0.0",
        port=port,
        reload=True,
    )
