"""
Fact Check Service
Service tìm kiếm thông tin liên quan
"""

import re
from typing import List, Dict, Any, Tuple
from datetime import datetime
import aiohttp


class FactCheckService:
    """Service tìm kiếm và xử lý thông tin"""
    
    def __init__(self):
        self.session: aiohttp.ClientSession | None = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """
        Trích xuất keywords từ text
        """
        # Vietnamese + English stopwords
        stopwords = {
            'là', 'và', 'của', 'có', 'được', 'trong', 'đã', 'cho', 'với', 'các',
            'một', 'này', 'đó', 'những', 'cũng', 'không', 'về', 'để', 'từ', 'trên',
            'hay', 'khi', 'nhưng', 'hoặc', 'nếu', 'thì', 'mà', 'vì', 'nên', 'sẽ',
            'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
            'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
            'might', 'can', 'a', 'an', 'and', 'or', 'but', 'if', 'then', 'so', 'as',
            'at', 'by', 'for', 'from', 'in', 'of', 'on', 'to', 'with'
        }
        
        # Tokenize
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter
        keywords = [w for w in words if w not in stopwords and len(w) > 3]
        
        # Count frequency
        word_freq = {}
        for w in keywords:
            word_freq[w] = word_freq.get(w, 0) + 1
        
        # Sort by frequency
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        return [w for w, _ in sorted_words[:top_n]]
    
    def generate_search_queries(self, article: str, title: str = None) -> List[str]:
        """
        Sinh ra các query tìm kiếm
        """
        queries = []
        
        # Query 1: Title (nếu có)
        if title:
            queries.append(title)
        
        # Query 2: Top keywords
        keywords = self.extract_keywords(article, top_n=5)
        if keywords:
            queries.append(' '.join(keywords))
        
        # Query 3: First sentence
        sentences = article.split('.')
        if sentences and len(sentences[0]) > 10:
            first_sentence = sentences[0].strip()
            if len(first_sentence) > 200:
                first_sentence = first_sentence[:200]
            queries.append(first_sentence)
        
        # Query 4: Keywords phân tán hơn
        if len(keywords) > 3:
            queries.append(' '.join(keywords[1:4]))
        
        return queries[:3]  # Limit to 3 queries
    
    async def search_related_content(
        self,
        queries: List[str],
        include_sources: List[str],
        languages: List[str],
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Tìm kiếm nội dung liên quan
        """
        from services.enhanced_search import EnhancedSearchService
        
        all_results = []
        seen_urls = set()
        
        results_per_query = max_results // len(queries) if queries else max_results
        
        async with EnhancedSearchService() as search_service:
            for query in queries:
                try:
                    results = await search_service.search_all(
                        query=query,
                        max_results=results_per_query,
                        include_sources=include_sources,
                        languages=languages,
                    )
                    
                    for result in results:
                        url = result.get('url', '')
                        
                        # Deduplicate
                        if url in seen_urls:
                            continue
                        
                        seen_urls.add(url)
                        all_results.append(result)
                    
                    print(f"✅ Query '{query[:50]}...': {len(results)} results")
                    
                except Exception as e:
                    print(f"❌ Query failed '{query[:50]}...': {e}")
                    continue
        
        return all_results
    
    def convert_to_article_format(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Chuyển đổi search result sang format article chuẩn
        Trả về: {url, title, article, domain, created_at, author, platform, crawl_success, image_urls}
        """
        # Extract domain for platform
        from urllib.parse import urlparse
        try:
            parsed = urlparse(result.get('url', ''))
            domain = parsed.netloc
            
            # Clean domain (remove www.)
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Determine platform
            if 'facebook.com' in domain:
                platform = 'facebook'
            elif 'twitter.com' in domain or 'x.com' in domain:
                platform = 'twitter'
            elif 'youtube.com' in domain or 'youtu.be' in domain:
                platform = 'youtube'
            elif 'tiktok.com' in domain:
                platform = 'tiktok'
            elif 'reddit.com' in domain:
                platform = 'reddit'
            else:
                platform = 'web'
        except:
            domain = 'unknown'
            platform = 'web'
        
        # Format created_at
        created_at = None
        if result.get('published_time'):
            try:
                pub_time = result['published_time']
                if isinstance(pub_time, str):
                    created_at = pub_time
                elif isinstance(pub_time, datetime):
                    created_at = pub_time.isoformat() + 'Z'
            except:
                pass
        
        # Get full article content and clean it
        raw_content = result.get('content')  # Full content từ crawler
        
        # Clean HTML tags và normalize text
        article = None
        if raw_content:
            import re
            import html
            
            # Decode HTML entities
            text = html.unescape(raw_content)
            
            # Remove script, style, navigation
            text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<nav[^>]*>.*?</nav>', '', text, flags=re.DOTALL | re.IGNORECASE)
            
            # Remove all HTML tags
            text = re.sub(r'<[^>]+>', ' ', text)
            
            # Remove URLs
            text = re.sub(r'http[s]?://\S+', '', text)
            
            # Clean multiple spaces
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            
            # Only keep if has meaningful content
            if len(text) > 100:
                article = text
        
        # Check crawl success
        crawl_success = article is not None and len(article) > 100
        
        # Extract image URLs (giả định trong tương lai)
        image_urls = []
        
        return {
            'url': result.get('url', ''),
            'title': result.get('title', 'No title'),
            'article': article,  # Clean plain text (có thể None nếu chưa crawl)
            'domain': domain,
            'created_at': created_at,
            'author': result.get('author'),
            'platform': platform,
            'crawl_success': crawl_success,
            'image_urls': image_urls
        }
