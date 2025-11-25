"""
Simple Content Crawler
Crawl full content từ URLs tìm được
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from urllib.parse import urlparse
import re

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode


class SimpleContentCrawler:
    """Service crawl nội dung từ URLs"""
    
    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
        self.browser_config = BrowserConfig(
            headless=True,
            verbose=False,
            extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
        )
        
        self.crawler_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            word_count_threshold=20,
            page_timeout=15000,  # 15s timeout
        )
    
    async def crawl_all(
        self,
        search_results: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Crawl all URLs from search results
        
        Returns:
            List of dicts với full content added
        """
        # Use a single browser instance for all crawls
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            tasks = [
                self._crawl_single(crawler, result)
                for result in search_results
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter valid results
        valid_results = []
        for result in results:
            if isinstance(result, dict) and result.get('url'):
                valid_results.append(result)
        
        return valid_results
    
    async def _crawl_single(self, crawler: AsyncWebCrawler, search_result: Dict[str, Any]) -> Dict[str, Any]:
        """Crawl một URL"""
        
        async with self.semaphore:
            url = search_result.get('url', '')
            
            if not url:
                return search_result
            
            try:
                # Use the shared crawler instance
                result = await crawler.arun(url=url, config=self.crawler_config)
                
                if not result.success:
                    # Return original with error
                    search_result['crawl_success'] = False
                    search_result['crawl_error'] = result.error_message
                    search_result['content'] = None
                    return search_result
                
                # Extract content
                title = result.metadata.get('title', search_result.get('title', ''))
                content = result.markdown.raw_markdown
                
                # Detect language
                language = self._detect_language(content)
                
                # Count words
                word_count = len(content.split())
                
                # Try to extract author from metadata
                author = result.metadata.get('author') or self._extract_author(content)
                
                # Try to extract publish time
                published_time = self._extract_publish_time(result.metadata)
                
                # Update search result with crawled data
                search_result.update({
                    'title': title,
                    'content': content[:50000],  # Limit to 50k chars
                    'author': author,
                    'published_time': published_time,
                    'language': language,
                    'word_count': word_count,
                    'crawled_at': datetime.utcnow().isoformat(),
                    'crawl_success': True,
                    'crawl_error': None,
                })
                
                return search_result
            
            except asyncio.TimeoutError:
                search_result['crawl_success'] = False
                search_result['crawl_error'] = "Timeout"
                search_result['content'] = None
                return search_result
            
            except Exception as e:
                search_result['crawl_success'] = False
                search_result['crawl_error'] = str(e)
                search_result['content'] = None
                return search_result
    
    def _detect_language(self, content: str) -> str:
        """Detect language"""
        vietnamese_chars = re.findall(
            r'[àáảãạăắằẳẵặâấầẩẫậđèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵ]',
            content.lower()
        )
        
        if len(vietnamese_chars) > len(content) * 0.02:
            return "vi"
        else:
            return "en"
    
    def _extract_author(self, content: str) -> Optional[str]:
        """Try to extract author from content"""
        # Look for common author patterns
        author_patterns = [
            r'(?:Tác giả|Author|By|Người viết)[\s:]+([A-ZÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬĐÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴ][a-zA-Zàáảãạăắằẳẵặâấầẩẫậđèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵ\s]{2,40})',
        ]
        
        for pattern in author_patterns:
            match = re.search(pattern, content[:2000], re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_publish_time(self, metadata: Dict[str, Any]) -> Optional[str]:
        """Extract publish time from metadata"""
        date_str = metadata.get('published_date') or metadata.get('date')
        
        if date_str:
            try:
                from dateutil import parser
                dt = parser.parse(date_str)
                return dt.isoformat()
            except:
                pass
        
        return None
