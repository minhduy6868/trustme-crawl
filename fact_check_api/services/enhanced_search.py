"""
Enhanced Multi-Source Search Service
Tìm kiếm từ nhiều nguồn: Google, Facebook, Twitter/X, Reddit, News, YouTube, etc.
"""

import asyncio
import re
import random
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus, urlparse
from datetime import datetime, timezone
from ddgs import DDGS


class EnhancedSearchService:
    """Service tìm kiếm đa nguồn mạnh mẽ"""
    
    def __init__(self):
        self.max_retries = 3
        self.semaphore = asyncio.Semaphore(5) # Higher concurrency allowed with library
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    async def search_all(
        self,
        query: str,
        max_results: int = 100,
        include_sources: List[str] = None,
        languages: List[str] = ["vi", "en"]
    ) -> List[Dict[str, Any]]:
        """
        Tìm kiếm từ tất cả nguồn
        
        Args:
            query: Từ khóa tìm kiếm
            max_results: Số kết quả tối đa
            include_sources: Danh sách nguồn cần tìm
            languages: Ngôn ngữ
            
        Returns:
            List các kết quả với url, title, snippet, source, etc.
        """
        if include_sources is None:
            include_sources = ["google", "facebook", "twitter", "reddit", "news"]
        
        # Normalize sources
        if "all" in include_sources:
            include_sources = ["google", "facebook", "twitter", "reddit", "news", "youtube", "tiktok", "instagram", "linkedin"]
        
        # Allocate more results for social platforms
        results_per_source = max(15, max_results // len(include_sources))
        
        tasks = []
        
        # Google search (general)
        if "google" in include_sources:
            tasks.append(self._search_google(query, results_per_source, languages))
        
        # Google News
        if "news" in include_sources:
            tasks.append(self._search_google_news(query, results_per_source, languages))
        
        # Facebook
        if "facebook" in include_sources:
            tasks.append(self._search_facebook(query, results_per_source, languages))
        
        # Twitter/X
        if "twitter" in include_sources or "x" in include_sources:
            tasks.append(self._search_twitter(query, results_per_source, languages))
        
        # Instagram
        if "instagram" in include_sources:
            tasks.append(self._search_instagram(query, results_per_source, languages))
        
        # LinkedIn
        if "linkedin" in include_sources:
            tasks.append(self._search_linkedin(query, results_per_source))
        
        # Reddit
        if "reddit" in include_sources:
            tasks.append(self._search_reddit(query, results_per_source))
        
        # YouTube
        if "youtube" in include_sources:
            tasks.append(self._search_youtube(query, results_per_source, languages))
        
        # TikTok
        if "tiktok" in include_sources:
            tasks.append(self._search_tiktok(query, results_per_source))
        
        # Government sites (.gov, .gov.vn)
        if "government" in include_sources or "gov" in include_sources:
            tasks.append(self._search_government_sites(query, languages))
        
        # Execute all searches in parallel
        results_batches = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine and deduplicate
        all_results = []
        seen_urls = set()
        
        for batch in results_batches:
            if isinstance(batch, list):
                for result in batch:
                    url = result.get('url', '')
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        all_results.append(result)
        
        return all_results[:max_results]
    
    async def _search_ddg_wrapper(self, query: str, max_results: int, region: str = "wt-wt") -> List[Dict[str, Any]]:
        """Wrapper for DDGS text search running in thread"""
        def run_search():
            results = []
            try:
                with DDGS() as ddgs:
                    # Use 'lite' backend for speed and reliability if needed, or 'auto'
                    ddg_results = ddgs.text(query, region=region, max_results=max_results, backend="auto")
                    if ddg_results:
                        for r in ddg_results:
                            results.append({
                                'url': r.get('href', ''),
                                'title': r.get('title', ''),
                                'snippet': r.get('body', ''),
                                'source': 'duckduckgo',
                                'found_at': datetime.now(timezone.utc).isoformat(),
                                'domain': self._extract_domain(r.get('href', ''))
                            })
            except Exception as e:
                print(f"DDGS error for '{query}': {e}")
            return results

        return await asyncio.to_thread(run_search)

    async def _search_google(
        self, 
        query: str, 
        max_results: int = 20,
        languages: List[str] = ["vi"]
    ) -> List[Dict[str, Any]]:
        """Tìm kiếm Google (via DuckDuckGo)"""
        region = "vn-vi" if "vi" in languages else "wt-wt"
        results = await self._search_ddg_wrapper(query, max_results, region)
        
        # Update source
        for r in results:
            r['source'] = 'google'
            
        return results
    
    async def _search_google_news(
        self,
        query: str,
        max_results: int = 20,
        languages: List[str] = ["vi"]
    ) -> List[Dict[str, Any]]:
        """Tìm kiếm Google News"""
        news_query = f"{query} tin tức" if "vi" in languages else f"{query} news"
        results = await self._search_google(news_query, max_results, languages)
        
        # Mark as news source
        for result in results:
            result['source'] = 'news'
        
        return results
    
    async def _search_facebook(
        self,
        query: str,
        max_results: int = 20,
        languages: List[str] = ["vi"]
    ) -> List[Dict[str, Any]]:
        """Tìm kiếm Facebook"""
        site_query = f"{query} site:facebook.com"
        results = await self._search_ddg_wrapper(site_query, max_results)
        
        # Update source
        for r in results:
            r['source'] = 'facebook'
            
        return results
    
    async def _search_twitter(
        self,
        query: str,
        max_results: int = 20,
        languages: List[str] = ["vi"]
    ) -> List[Dict[str, Any]]:
        """Tìm kiếm Twitter/X"""
        site_query = f"{query} (site:twitter.com OR site:x.com)"
        results = await self._search_ddg_wrapper(site_query, max_results)
        
        # Update source
        for r in results:
            r['source'] = 'twitter'
            
        return results
    
    async def _search_reddit(
        self,
        query: str,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """Tìm kiếm Reddit"""
        site_query = f"{query} site:reddit.com"
        results = await self._search_ddg_wrapper(site_query, max_results)
        
        # Update source
        for r in results:
            r['source'] = 'reddit'
            
        return results
    
    async def _search_youtube(
        self,
        query: str,
        max_results: int = 20,
        languages: List[str] = ["vi"]
    ) -> List[Dict[str, Any]]:
        """Tìm kiếm YouTube"""
        site_query = f"{query} site:youtube.com"
        results = await self._search_ddg_wrapper(site_query, max_results)
        
        # Update source
        for r in results:
            r['source'] = 'youtube'
            
        return results
    
    async def _search_tiktok(
        self,
        query: str,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """Tìm kiếm TikTok"""
        site_query = f"{query} site:tiktok.com"
        results = await self._search_ddg_wrapper(site_query, max_results)
        
        # Update source
        for r in results:
            r['source'] = 'tiktok'
            
        return results
    
    async def _search_instagram(
        self,
        query: str,
        max_results: int = 20,
        languages: List[str] = ["vi"]
    ) -> List[Dict[str, Any]]:
        """Tìm kiếm Instagram"""
        site_query = f"{query} site:instagram.com"
        results = await self._search_ddg_wrapper(site_query, max_results)
        
        # Update source
        for r in results:
            r['source'] = 'instagram'
            
        return results
    
    async def _search_linkedin(
        self,
        query: str,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """Tìm kiếm LinkedIn"""
        site_query = f"{query} site:linkedin.com"
        results = await self._search_ddg_wrapper(site_query, max_results)
        
        # Update source
        for r in results:
            r['source'] = 'linkedin'
            
        return results
    
    async def _search_government_sites(
        self,
        query: str,
        languages: List[str] = ["vi"]
    ) -> List[Dict[str, Any]]:
        """Tìm kiếm trang chính phủ"""
        results = []
        
        gov_domains = [
            "gov.vn",
            "chinhphu.vn",
            "baochinhphu.vn",
        ]
        
        for domain in gov_domains[:2]:
            site_query = f"{query} site:{domain}"
            domain_results = await self._search_ddg_wrapper(site_query, 10, region="vn-vi")
            
            for r in domain_results:
                r['source'] = 'government'
                
            results.extend(domain_results)
        
        return results
    

    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return ""
