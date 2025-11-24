"""
Fact Check API
API tìm kiếm và crawl thông tin liên quan từ một bài đăng/bài viết
"""

import sys
from pathlib import Path

# Add parent directory to Python path để import crawl4ai
parent_dir = str(Path(__file__).parent.parent.absolute())
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import asyncio
import time
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from models.fact_check_schemas import (
    ArticleAnalyzeRequest,
    ArticleAnalyzeResponse,
    SourceArticle,
    RelatedArticle,
    PaginationMeta,
)
from services.fact_check_service import FactCheckService
from services.simple_crawler import SimpleContentCrawler


# Initialize FastAPI
app = FastAPI(
    title="Fact Check API",
    description="API tìm kiếm và crawl thông tin liên quan từ bài đăng/bài viết",
    version="2.0.0",
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


@app.on_event("startup")
async def startup_event():
    """Initialize services"""
    global crawler_service
    crawler_service = SimpleContentCrawler(max_concurrent=10)
    print("✅ Fact Check API initialized")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Fact Check API",
        "version": "2.0.0",
        "description": "Tìm kiếm và crawl thông tin liên quan từ bài đăng/bài viết",
        "status": "operational",
        "endpoints": {
            "search": "POST /fact-check - Tìm kiếm thông tin liên quan",
            "health": "GET /health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check"""
    from datetime import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "crawler": crawler_service is not None,
        }
    }


@app.post("/api/article/analyze", response_model=ArticleAnalyzeResponse)
async def analyze_article(request: ArticleAnalyzeRequest):
    """
    Phân tích bài viết và tìm bài liên quan
    
    Input: Bài viết gốc
    Output: Bài viết gốc + danh sách bài liên quan (không giới hạn)
    """
    start_time = time.time()
    
    try:
        # Convert request to SourceArticle
        source_article = SourceArticle(
            url=request.url,
            title=request.title,
            article=request.article,
            created_at=request.created_at,
            author=request.author,
            platform=request.platform,
            image_urls=request.image_urls
        )
        
        # Step 1: Generate search queries
        print(f"🔍 Generating search queries from article...")
        async with FactCheckService() as fact_service:
            queries = fact_service.generate_search_queries(
                article=request.article,
                title=request.title
            )
        
        print(f"✅ Generated {len(queries)} queries")
        
        # Step 2: Search ALL sources by default (150 results for better social coverage)
        include_sources = ["google", "facebook", "twitter", "instagram", "linkedin", "reddit", "youtube", "tiktok", "news"]
        max_results = 150
        
        print(f"🌐 Searching across ALL sources: {', '.join(include_sources)}...")
        async with FactCheckService() as fact_service:
            search_results = await fact_service.search_related_content(
                queries=queries,
                include_sources=include_sources,
                languages=["vi", "en"],
                max_results=max_results
            )
        
        print(f"✅ Found {len(search_results)} results")
        
        # Step 3: Deep crawl (always enabled)
        if search_results:
            print(f"📥 Deep crawling {len(search_results)} URLs...")
            crawled_results = await crawler_service.crawl_all(search_results)
            print(f"✅ Crawled {len([r for r in crawled_results if r.get('crawl_success')])} successfully")
        else:
            crawled_results = []
        
        # Step 4: Convert to article format
        print(f"⚙️ Converting to article format...")
        async with FactCheckService() as fact_service:
            articles = [
                fact_service.convert_to_article_format(result)
                for result in crawled_results
            ]
        
        # Step 5: Create response (NO pagination - return all)
        related_articles = [
            RelatedArticle(**article)
            for article in articles
        ]
        
        response = ArticleAnalyzeResponse(
            main_search=source_article,
            data=related_articles,
            meta=PaginationMeta(
                page=1,
                limit=10,
                total=len(related_articles),
                has_next=False
            )
        )
        
        elapsed = time.time() - start_time
        print(f"✅ Completed in {elapsed:.2f}s - Found {len(related_articles)} related articles")
        
        return response
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Article analyze failed: {str(e)}")


# ==================== RUN SERVER ====================

if __name__ == "__main__":
    import os
    port = int(os.getenv("API_PORT", 8001))
    uvicorn.run(
        app,  # Use app object directly
        host="0.0.0.0",
        port=port,
        reload=False,
    )
