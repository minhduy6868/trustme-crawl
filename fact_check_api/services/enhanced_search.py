"""
Enhanced Multi-Source Search Service
Tìm kiếm từ nhiều nguồn: Google, Facebook, Twitter/X, Reddit, News, YouTube, etc.
"""

import asyncio
import re
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus, urlparse
import aiohttp
from datetime import datetime


class EnhancedSearchService:
    """Service tìm kiếm đa nguồn mạnh mẽ"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limit_delay = 0.5  # Delay giữa các requests
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.max_retries = 2
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
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
    
    async def _search_google(
        self, 
        query: str, 
        max_results: int = 20,
        languages: List[str] = ["vi"]
    ) -> List[Dict[str, Any]]:
        """Tìm kiếm Google (via DuckDuckGo)"""
        results = []
        
        try:
            encoded_query = quote_plus(query)
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    results = self._parse_duckduckgo_html(html, source="google")
            
            await asyncio.sleep(self.rate_limit_delay)
            
        except Exception as e:
            print(f"Google search error: {e}")
        
        return results[:max_results]
    
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
        """Tìm kiếm Facebook - Tăng cường với nhiều chiến lược"""
        results = []
        
        try:
            # Strategy 1: Direct Facebook search via DuckDuckGo
            site_query = f"{query} site:facebook.com"
            encoded_query = quote_plus(site_query)
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    results = self._parse_duckduckgo_html(html, source="facebook")
            
            await asyncio.sleep(self.rate_limit_delay)
            
            # Strategy 2: Search Facebook pages và posts riêng
            if len(results) < max_results:
                page_query = f"{query} site:facebook.com/*/posts OR site:m.facebook.com"
                encoded_query = quote_plus(page_query)
                url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
                
                async with self.session.get(url, headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        more_results = self._parse_duckduckgo_html(html, source="facebook")
                        
                        # Deduplicate
                        existing_urls = {r['url'] for r in results}
                        for r in more_results:
                            if r['url'] not in existing_urls:
                                results.append(r)
                                existing_urls.add(r['url'])
                
                await asyncio.sleep(self.rate_limit_delay)
            
        except Exception as e:
            print(f"Facebook search error: {e}")
        
        return results[:max_results]
    
    async def _search_twitter(
        self,
        query: str,
        max_results: int = 20,
        languages: List[str] = ["vi"]
    ) -> List[Dict[str, Any]]:
        """Tìm kiếm Twitter/X - Tăng cường nhiều chiến lược"""
        results = []
        
        try:
            # Strategy 1: Search both twitter.com và x.com
            site_query = f"{query} (site:twitter.com OR site:x.com)"
            encoded_query = quote_plus(site_query)
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    results = self._parse_duckduckgo_html(html, source="twitter")
            
            await asyncio.sleep(self.rate_limit_delay)
            
            # Strategy 2: Search với hashtags nếu có
            if '#' not in query and len(results) < max_results:
                hashtag_query = f"#{query.replace(' ', '')} site:twitter.com OR site:x.com"
                encoded_query = quote_plus(hashtag_query)
                url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
                
                async with self.session.get(url, headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        more_results = self._parse_duckduckgo_html(html, source="twitter")
                        
                        # Deduplicate
                        existing_urls = {r['url'] for r in results}
                        for r in more_results:
                            if r['url'] not in existing_urls:
                                results.append(r)
                                existing_urls.add(r['url'])
                
                await asyncio.sleep(self.rate_limit_delay)
            
        except Exception as e:
            print(f"Twitter search error: {e}")
        
        return results[:max_results]
    
    async def _search_reddit(
        self,
        query: str,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """Tìm kiếm Reddit"""
        results = []
        
        try:
            site_query = f"{query} site:reddit.com"
            encoded_query = quote_plus(site_query)
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    results = self._parse_duckduckgo_html(html, source="reddit")
            
            await asyncio.sleep(self.rate_limit_delay)
            
        except Exception as e:
            print(f"Reddit search error: {e}")
        
        return results[:max_results]
    
    async def _search_youtube(
        self,
        query: str,
        max_results: int = 20,
        languages: List[str] = ["vi"]
    ) -> List[Dict[str, Any]]:
        """Tìm kiếm YouTube"""
        results = []
        
        try:
            site_query = f"{query} site:youtube.com"
            encoded_query = quote_plus(site_query)
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    results = self._parse_duckduckgo_html(html, source="youtube")
            
            await asyncio.sleep(self.rate_limit_delay)
            
        except Exception as e:
            print(f"YouTube search error: {e}")
        
        return results[:max_results]
    
    async def _search_tiktok(
        self,
        query: str,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """Tìm kiếm TikTok"""
        results = []
        
        try:
            site_query = f"{query} site:tiktok.com"
            encoded_query = quote_plus(site_query)
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    results = self._parse_duckduckgo_html(html, source="tiktok")
            
            await asyncio.sleep(self.rate_limit_delay)
            
        except Exception as e:
            print(f"TikTok search error: {e}")
        
        return results[:max_results]
    
    async def _search_instagram(
        self,
        query: str,
        max_results: int = 20,
        languages: List[str] = ["vi"]
    ) -> List[Dict[str, Any]]:
        """Tìm kiếm Instagram"""
        results = []
        
        try:
            # Search Instagram posts
            site_query = f"{query} site:instagram.com"
            encoded_query = quote_plus(site_query)
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    results = self._parse_duckduckgo_html(html, source="instagram")
            
            await asyncio.sleep(self.rate_limit_delay)
            
        except Exception as e:
            print(f"Instagram search error: {e}")
        
        return results[:max_results]
    
    async def _search_linkedin(
        self,
        query: str,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """Tìm kiếm LinkedIn"""
        results = []
        
        try:
            # Search LinkedIn posts and articles
            site_query = f"{query} site:linkedin.com"
            encoded_query = quote_plus(site_query)
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    results = self._parse_duckduckgo_html(html, source="linkedin")
            
            await asyncio.sleep(self.rate_limit_delay)
            
        except Exception as e:
            print(f"LinkedIn search error: {e}")
        
        return results[:max_results]
    
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
        
        for domain in gov_domains[:2]:  # Limit để tránh quá nhiều requests
            try:
                site_query = f"{query} site:{domain}"
                encoded_query = quote_plus(site_query)
                url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                async with self.session.get(url, headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        domain_results = self._parse_duckduckgo_html(html, source="government")
                        results.extend(domain_results)
                
                await asyncio.sleep(self.rate_limit_delay)
                
            except Exception as e:
                print(f"Government site search error for {domain}: {e}")
        
        return results
    
    def _parse_duckduckgo_html(self, html: str, source: str = "google") -> List[Dict[str, Any]]:
        """Parse DuckDuckGo HTML results"""
        results = []
        
        # Extract links and titles
        link_pattern = r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>([^<]+)</a>'
        snippet_pattern = r'<a[^>]+class="result__snippet"[^>]*>([^<]+)</a>'
        
        links = re.findall(link_pattern, html)
        snippets = re.findall(snippet_pattern, html)
        
        for i, (url, title) in enumerate(links[:50]):
            # Clean URL (remove DuckDuckGo redirect)
            if '//duckduckgo.com/l/?' in url:
                match = re.search(r'uddg=([^&]+)', url)
                if match:
                    from urllib.parse import unquote
                    url = unquote(match.group(1))
            
            # Skip if URL is invalid
            if not url or not url.startswith('http'):
                continue
            
            snippet = snippets[i] if i < len(snippets) else ""
            
            # Extract domain
            domain = self._extract_domain(url)
            
            results.append({
                'url': url,
                'title': title.strip(),
                'snippet': snippet.strip(),
                'source': source,
                'domain': domain,
                'found_at': datetime.utcnow().isoformat(),
            })
        
        return results
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return ""
