"""
Simple Content Crawler
Crawl full content từ URLs tìm được
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
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
            extra_args=[
                "--disable-gpu", 
                "--disable-dev-shm-usage", 
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled"
            ],
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
        tasks = [
            self._crawl_single(result)
            for result in search_results
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter valid results
        valid_results = []
        for result in results:
            if isinstance(result, dict) and result.get('url'):
                valid_results.append(result)
        
        return valid_results
    
    async def _crawl_single(self, search_result: Dict[str, Any]) -> Dict[str, Any]:
        """Crawl một URL - Enhanced với social media handling"""
        
        async with self.semaphore:
            url = search_result.get('url', '')
            
            if not url or not url.startswith(('http://', 'https://')):
                search_result['crawl_success'] = False
                search_result['crawl_error'] = "Invalid URL"
                search_result['content'] = None
                return search_result
            
            # Detect platform from URL
            platform = self._detect_platform(url)
            
            # Social media platforms cần xử lý đặc biệt
            if platform in ['facebook', 'twitter', 'instagram', 'linkedin']:
                return await self._crawl_social_media(search_result, url, platform)
            else:
                return await self._crawl_web(search_result, url)
    
    async def _crawl_web(self, search_result: Dict[str, Any], url: str) -> Dict[str, Any]:
        """Crawl regular web pages"""
        try:
            async with AsyncWebCrawler(config=self.browser_config) as crawler:
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
                    'crawled_at': datetime.now(timezone.utc).isoformat(),
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
    
    async def _crawl_social_media(
        self, 
        search_result: Dict[str, Any], 
        url: str, 
        platform: str
    ) -> Dict[str, Any]:
        """Crawl social media - Enhanced với custom config"""
        try:
            # Social media needs special browser config
            social_browser_config = BrowserConfig(
                headless=True,
                verbose=False,
                extra_args=[
                    "--disable-gpu",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                    "--disable-blink-features=AutomationControlled",
                ],
            )
            
            social_crawler_config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                word_count_threshold=10,  # Lower threshold cho social
                page_timeout=30000,  # Longer timeout cho social
                wait_for="networkidle",  # Wait for network idle
                delay_before_return_html=3.0,  # Extra delay để load dynamic content
            )
            
            async with AsyncWebCrawler(config=social_browser_config) as crawler:
                result = await crawler.arun(url=url, config=social_crawler_config)
                
                if not result.success:
                    search_result['crawl_success'] = False
                    search_result['crawl_error'] = result.error_message
                    search_result['content'] = None
                    return search_result
                
                # Extract content with platform-specific parsing
                title = result.metadata.get('title', search_result.get('title', ''))
                raw_content = result.markdown.raw_markdown
                
                # Platform-specific content extraction
                content = self._extract_social_content(raw_content, platform)
                
                # Detect language
                language = self._detect_language(content)
                
                # Word count
                word_count = len(content.split())
                
                # Extract author
                author = self._extract_social_author(result.metadata, platform)
                
                # Extract publish time
                published_time = self._extract_publish_time(result.metadata)
                
                # Update result
                search_result.update({
                    'title': title,
                    'content': content[:50000],
                    'author': author,
                    'published_time': published_time,
                    'language': language,
                    'word_count': word_count,
                    'crawled_at': datetime.now(timezone.utc).isoformat(),
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
    
    def _detect_platform(self, url: str) -> str:
        """Detect platform from URL"""
        url_lower = url.lower()
        if 'facebook.com' in url_lower or 'fb.com' in url_lower:
            return 'facebook'
        elif 'twitter.com' in url_lower or 'x.com' in url_lower:
            return 'twitter'
        elif 'instagram.com' in url_lower:
            return 'instagram'
        elif 'linkedin.com' in url_lower:
            return 'linkedin'
        elif 'youtube.com' in url_lower or 'youtu.be' in url_lower:
            return 'youtube'
        elif 'tiktok.com' in url_lower:
            return 'tiktok'
        elif 'reddit.com' in url_lower:
            return 'reddit'
        else:
            return 'web'
    
    def _extract_social_content(self, raw_content: str, platform: str) -> str:
        """Extract relevant content from social media markdown"""
        import re
        
        # Remove common social media noise
        content = raw_content
        
        # Remove markdown links [text](url)
        content = re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', content)
        
        # Remove navigation menus
        content = re.sub(r'(?i)(home|profile|messages|notifications|settings)[\s\n]+', '', content)
        
        # Remove repeated social UI elements
        content = re.sub(r'(?i)(like|share|comment|retweet|follow)[\s\n]+', '', content)
        
        # Remove common Wikipedia/website navigation
        content = re.sub(r'(?i)(bước tới nội dung|trình đơn|menu|navigation|sidebar)[\s\n]+', '', content)
        content = re.sub(r'(?i)(search|login|sign up|register|đăng nhập|đăng ký)[\s\n]+', '', content)
        
        # Platform-specific cleaning
        if platform == 'facebook':
            # Remove Facebook UI noise
            content = re.sub(r'(?i)(see more|see less|most relevant)[\s\n]+', '', content)
        elif platform == 'twitter':
            # Remove Twitter UI noise
            content = re.sub(r'(?i)(show this thread|replying to @\w+)[\s\n]+', '', content)
        elif platform == 'instagram':
            # Remove Instagram UI noise
            content = re.sub(r'(?i)(view all \d+ comments)[\s\n]+', '', content)
        
        # Remove repeated special characters
        content = re.sub(r'[\[\]\(\)\*\#\-\=]{3,}', '', content)
        
        # Clean up multiple spaces and newlines
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content.strip()
    
    def _extract_social_author(self, metadata: Dict[str, Any], platform: str) -> Optional[str]:
        """Extract author from social media metadata"""
        author = metadata.get('author')
        
        if not author:
            # Try to extract from other metadata fields
            if platform == 'twitter':
                author = metadata.get('twitter:creator')
            elif platform == 'facebook':
                author = metadata.get('article:author')
        
        return author
    
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
