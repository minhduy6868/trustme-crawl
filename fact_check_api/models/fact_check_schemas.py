"""
Fact Check API Schemas
Tìm kiếm và crawl thông tin liên quan từ một bài đăng
"""

from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field


# ==================== INPUT MODEL ====================

class SourceArticle(BaseModel):
    """Bài viết/bài đăng đầu vào"""
    url: str = Field(..., description="URL của bài đăng gốc")
    title: Optional[str] = Field(None, description="Tiêu đề (nếu có)")
    article: str = Field(..., description="Nội dung bài đăng/bài viết")
    created_at: Optional[str] = Field(None, description="Thời gian đăng ISO format")
    author: Optional[str] = Field(None, description="Tác giả/người đăng")
    platform: str = Field(..., description="Nền tảng: facebook, web, twitter, etc.")
    image_urls: List[str] = Field(default_factory=list, description="Danh sách URL ảnh")
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://www.facebook.com/user/posts/123456789",
                "title": None,
                "article": "Đây là nội dung bài đăng trên Facebook.",
                "created_at": "2024-11-23T08:30:00.000Z",
                "author": "Nguyễn Văn A",
                "platform": "facebook",
                "image_urls": []
            }
        }


class ArticleAnalyzeRequest(BaseModel):
    """Request phân tích bài viết - Chỉ cần bài viết gốc"""
    url: str = Field(..., description="URL của bài đăng gốc")
    title: Optional[str] = Field(None, description="Tiêu đề (nếu có)")
    article: str = Field(..., description="Nội dung bài đăng/bài viết")
    created_at: Optional[str] = Field(None, description="Thời gian đăng ISO format")
    author: Optional[str] = Field(None, description="Tác giả/người đăng")
    platform: str = Field(..., description="Nền tảng: facebook, web, twitter, etc.")
    image_urls: List[str] = Field(default_factory=list, description="Danh sách URL ảnh")
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://test.com",
                "title": "COVID-19 vaccine",
                "article": "Vaccine COVID-19 thế hệ mới được phê duyệt tại Việt Nam",
                "created_at": None,
                "author": None,
                "platform": "web",
                "image_urls": []
            }
        }


# ==================== OUTPUT MODEL ====================

class RelatedArticle(BaseModel):
    """Bài viết liên quan tìm được"""
    url: str = Field(..., description="URL")
    title: str = Field(..., description="Tiêu đề")
    article: Optional[str] = Field(None, description="Nội dung đầy đủ (nếu crawl thành công)")
    domain: str = Field(..., description="Tên miền (ví dụ: vnexpress.net)")
    created_at: Optional[str] = Field(None, description="Thời gian đăng ISO format")
    author: Optional[str] = Field(None, description="Tác giả")
    platform: str = Field(..., description="Nền tảng")
    crawl_success: bool = Field(default=False, description="Có crawl thành công không")
    image_urls: List[str] = Field(default_factory=list, description="Danh sách ảnh")
    first_seen: Optional[str] = Field(None, description="Lần đầu phát hiện")
    last_seen: Optional[str] = Field(None, description="Lần cuối phát hiện")
    share_count: int = Field(default=0, description="Số lượt chia sẻ/bài liên quan")
    is_verified_account: bool = Field(default=False, description="Tài khoản đã xác minh")
    screenshot_hash: Optional[str] = Field(None, description="Hash ảnh chụp màn hình")
    fingerprint: Optional[str] = Field(None, description="Fingerprint nội dung")
    duplicate_of: Optional[str] = Field(None, description="Nếu là trùng lặp, URL gốc")


class PaginationMeta(BaseModel):
    """Thông tin phân trang"""
    page: int = Field(default=1, description="Trang hiện tại")
    limit: int = Field(default=10, description="Số item mỗi trang")
    total: int = Field(..., description="Tổng số item trả về")
    has_next: bool = Field(default=False, description="Có trang tiếp theo không")
    domain_frequency: Dict[str, int] = Field(default_factory=dict, description="Số lượng kết quả theo domain")


class ArticleAnalyzeResponse(BaseModel):
    """Response trả về từ API analyze"""
    main_search: SourceArticle = Field(..., description="Bài viết gốc (echo lại)")
    data: List[RelatedArticle] = Field(default_factory=list, description="Danh sách bài viết liên quan (không giới hạn)")
    meta: PaginationMeta = Field(..., description="Thông tin phân trang")
    
    class Config:
        json_schema_extra = {
            "example": {
                "main_search": {
                    "url": "https://example.com/article",
                    "title": "Tiêu đề bài báo",
                    "article": "Nội dung...",
                    "platform": "web"
                },
                "data": [],
                "meta": {
                    "page": 1,
                    "limit": 10,
                    "total": 10,
                    "has_next": False,
                    "total_found": 50,
                    "domain_frequency": {}
                }
            }
        }
