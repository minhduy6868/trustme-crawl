"""
Simple Search API Schemas
Tìm kiếm và tổng hợp thông tin từ nhiều nguồn trên Internet
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


# ==================== INPUT MODELS ====================

class ModelProcessingOptions(BaseModel):
    """Tùy chọn xử lý cho downstream model (LLM, reranker, etc.)"""
    enabled: bool = Field(
        default=False,
        description="Bật chuẩn bị dữ liệu cho model xử lý sau khi crawl"
    )
    chunk_size: int = Field(
        default=1200,
        description="Kích thước chunk (ký tự) gửi vào model",
        ge=200,
        le=4000,
    )
    chunk_overlap: int = Field(
        default=150,
        description="Phần trùng lặp giữa các chunk (ký tự)",
        ge=0,
        le=1000,
    )
    max_chunks: int = Field(
        default=200,
        description="Giới hạn số chunk tối đa gửi vào model",
        ge=1,
        le=2000,
    )
    max_parallel_workers: int = Field(
        default=4,
        description="Số worker tối đa xử lý song song phía model",
        ge=1,
        le=32,
    )
    summarize: bool = Field(
        default=True,
        description="Model sẽ sinh summary/tóm tắt"
    )
    rerank: bool = Field(
        default=False,
        description="Model rerank kết quả trước khi trả về"
    )
    stream_output: bool = Field(
        default=True,
        description="Cho phép stream kết quả model từng phần ra frontend"
    )


class SearchRequest(BaseModel):
    """Request model for multi-source search"""
    query: str = Field(
        ..., 
        description="Từ khóa tìm kiếm - keywords, tác giả, chủ đề, v.v.",
        min_length=2,
        max_length=500
    )
    
    # Search options
    max_results: int = Field(
        default=100, 
        description="Số lượng kết quả tối đa", 
        ge=10, 
        le=500
    )
    
    include_sources: List[str] = Field(
        default=["google", "facebook", "twitter", "reddit", "news", "youtube"],
        description="Nguồn tìm kiếm: google, facebook, twitter, reddit, news, youtube, all"
    )
    
    languages: List[str] = Field(
        default=["vi", "en"], 
        description="Ngôn ngữ tìm kiếm"
    )
    
    deep_crawl: bool = Field(
        default=True,
        description="Crawl đầy đủ nội dung (chậm hơn nhưng đầy đủ hơn)"
    )
    
    timeout: int = Field(
        default=300, 
        description="Timeout tính bằng giây", 
        ge=30, 
        le=600
    )
    
    model_options: ModelProcessingOptions = Field(
        default_factory=ModelProcessingOptions,
        description="Cấu hình chuẩn bị dữ liệu để đưa vào downstream model"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "AI trong giáo dục Việt Nam",
                "max_results": 100,
                "include_sources": ["google", "facebook", "twitter", "news"],
                "languages": ["vi"],
                "deep_crawl": True,
                "model_options": {
                    "enabled": True,
                    "chunk_size": 1500,
                    "chunk_overlap": 200,
                    "summarize": True,
                    "rerank": True
                }
            }
        }


# ==================== OUTPUT MODELS ====================

class SearchResult(BaseModel):
    """Kết quả tìm kiếm từ một nguồn"""
    
    # Basic info
    title: str = Field(..., description="Tiêu đề")
    content: Optional[str] = Field(None, description="Nội dung đầy đủ (nếu crawl được)")
    snippet: Optional[str] = Field(None, description="Đoạn trích ngắn")
    
    # Author and time
    author: Optional[str] = Field(None, description="Tác giả / Người đăng")
    published_time: Optional[datetime] = Field(None, description="Thời gian đăng")
    
    # URL and source
    url: str = Field(..., description="Link nguồn")
    source: str = Field(..., description="Nguồn: google, facebook, twitter, etc.")
    domain: str = Field(..., description="Tên miền: vnexpress.net, facebook.com, etc.")
    
    # Trust and credibility
    url_trust: bool = Field(
        default=False, 
        description="Nguồn tin cậy (gov, news chính thống) = True, social media = False"
    )
    trust_score: float = Field(
        default=50.0, 
        description="Điểm tin cậy 0-100",
        ge=0.0,
        le=100.0
    )
    
    # Metadata
    language: Optional[str] = Field(None, description="Ngôn ngữ phát hiện")
    word_count: Optional[int] = Field(None, description="Số lượng từ trong content")
    
    # Social metrics (if available)
    likes: Optional[int] = Field(None, description="Số lượt thích (Facebook, etc.)")
    shares: Optional[int] = Field(None, description="Số lượt share")
    comments: Optional[int] = Field(None, description="Số comments")
    views: Optional[int] = Field(None, description="Số lượt xem (YouTube, etc.)")
    
    # Crawl info
    crawled_at: datetime = Field(default_factory=datetime.utcnow)
    crawl_success: bool = Field(default=True, description="Crawl thành công hay không")
    crawl_error: Optional[str] = Field(None, description="Lỗi khi crawl (nếu có)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Ứng dụng AI trong giáo dục Việt Nam",
                "content": "AI đang được áp dụng rộng rãi trong giáo dục...",
                "snippet": "AI đang thay đổi cách dạy và học...",
                "author": "Nguyễn Minh Duy",
                "published_time": "2025-10-29T10:35:00Z",
                "url": "https://www.facebook.com/page/posts/12345",
                "source": "facebook",
                "domain": "facebook.com",
                "url_trust": False,
                "trust_score": 30.0,
                "language": "vi",
                "likes": 150,
                "shares": 20,
                "comments": 35
            }
        }


class SearchStats(BaseModel):
    """Thống kê kết quả tìm kiếm"""
    total_found: int = Field(default=0, description="Tổng số kết quả tìm được")
    total_crawled: int = Field(default=0, description="Số kết quả crawl thành công")
    total_failed: int = Field(default=0, description="Số kết quả crawl thất bại")
    
    # By source
    by_source: Dict[str, int] = Field(
        default_factory=dict,
        description="Số lượng theo nguồn: {'google': 50, 'facebook': 30, ...}"
    )
    
    # By trust level
    trusted_sources: int = Field(default=0, description="Số nguồn tin cậy")
    untrusted_sources: int = Field(default=0, description="Số nguồn không tin cậy")
    
    # Processing time
    processing_time_seconds: float = Field(default=0.0, description="Thời gian xử lý (giây)")


class ModelChunk(BaseModel):
    """Chunk nội dung chuẩn bị cho downstream model"""
    chunk_id: str = Field(..., description="ID chunk")
    order: int = Field(..., description="Thứ tự chunk")
    request_id: str = Field(..., description="ID request gốc")
    source: str = Field(..., description="Nguồn crawl")
    domain: str = Field(..., description="Domain")
    trust_score: float = Field(..., description="Điểm tin cậy")
    text: str = Field(..., description="Nội dung chunk")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata bổ sung")


class ModelStatus(BaseModel):
    """Trạng thái xử lý của downstream model"""
    enabled: bool = Field(default=False, description="Model có được bật không")
    state: str = Field(
        default="disabled",
        description="Trạng thái: disabled, pending, queued, processing, completed, failed"
    )
    total_chunks: int = Field(default=0, description="Tổng số chunk")
    pending_chunks: int = Field(default=0, description="Chunk chờ xử lý")
    processed_chunks: int = Field(default=0, description="Chunk đã xử lý")
    concurrency_limit: int = Field(default=4, description="Giới hạn song song")
    last_error: Optional[str] = Field(None, description="Lỗi gần nhất (nếu có)")


class SearchResponse(BaseModel):
    """Response trả về từ API search"""
    
    # Request info
    request_id: str = Field(..., description="ID của request")
    query: str = Field(..., description="Query gốc")
    
    # Results
    results: List[SearchResult] = Field(
        default_factory=list,
        description="Danh sách kết quả tìm kiếm"
    )

    # Model-ready payload
    model_chunks: List[ModelChunk] = Field(
        default_factory=list,
        description="Danh sách chunk nội dung đã chuẩn hóa để đưa vào model"
    )
    model_status: ModelStatus = Field(
        default_factory=ModelStatus,
        description="Trạng thái xử lý của downstream model"
    )

    # Stats
    stats: SearchStats
    
    # Status
    status: str = Field(
        default="completed",
        description="Trạng thái: processing, completed, failed"
    )
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "search_abc123",
                "query": "AI trong giáo dục",
                "results": [
                    {
                        "title": "Ứng dụng AI...",
                        "content": "...",
                        "author": "Nguyen Van A",
                        "url": "https://...",
                        "source": "facebook",
                        "url_trust": False
                    }
                ],
                "stats": {
                    "total_found": 150,
                    "total_crawled": 145,
                    "trusted_sources": 50,
                    "untrusted_sources": 95
                },
                "model_status": {
                    "enabled": True,
                    "state": "queued",
                    "total_chunks": 12,
                    "pending_chunks": 12,
                    "processed_chunks": 0
                },
                "status": "completed"
            }
        }


# ==================== ASYNC RESPONSE ====================

class SearchProgress(BaseModel):
    """Progress update cho async search"""
    request_id: str
    stage: str = Field(..., description="Giai đoạn: searching, crawling, processing")
    progress: float = Field(..., description="Tiến độ % (0-100)", ge=0.0, le=100.0)
    message: str = Field(..., description="Thông báo tiến độ")
    current_results: int = Field(default=0, description="Số kết quả đã tìm được")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
