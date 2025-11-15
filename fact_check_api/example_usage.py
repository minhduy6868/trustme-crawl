"""
Example usage of Multi-Source Search API
"""

import requests
import json
import time
from typing import Dict, Any

API_BASE_URL = "http://localhost:8000"

def print_result(result: Dict[str, Any], index: int):
    """Pretty print a search result"""
    print(f"\n{'='*80}")
    print(f"📄 Result #{index}")
    print(f"{'='*80}")
    print(f"Title:      {result['title']}")
    print(f"URL:        {result['url']}")
    print(f"Source:     {result['source']}")
    print(f"Domain:     {result['domain']}")
    print(f"Trust:      {'✅ Trusted' if result['url_trust'] else '⚠️  Verify'} (Score: {result['trust_score']})")
    
    if result.get('author'):
        print(f"Author:     {result['author']}")
    
    if result.get('published_time'):
        print(f"Published:  {result['published_time']}")
    
    if result.get('word_count'):
        print(f"Words:      {result['word_count']}")
    
    if result.get('content'):
        content = result['content']
        preview = content[:300] + "..." if len(content) > 300 else content
        print(f"\nContent:\n{preview}")
    elif result.get('snippet'):
        print(f"\nSnippet:\n{result['snippet']}")

def example_sync_search():
    """Example: Synchronous search (wait for results)"""
    print("\n" + "="*80)
    print("🔍 Example 1: Synchronous Search")
    print("="*80)
    
    payload = {
        "query": "Python FastAPI tutorial",
        "max_results": 20,
        "include_sources": ["google", "reddit", "youtube"],
        "languages": ["en"],
        "deep_crawl": False  # Fast mode
    }
    
    print(f"\n📤 Sending request: {payload['query']}")
    print(f"   Sources: {', '.join(payload['include_sources'])}")
    print(f"   Max results: {payload['max_results']}")
    
    start_time = time.time()
    response = requests.post(f"{API_BASE_URL}/search", json=payload)
    elapsed = time.time() - start_time
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Completed in {elapsed:.2f}s")
        print(f"📊 Found {len(data['results'])} results")
        
        # Print stats
        stats = data.get('stats', {})
        print(f"\n📈 Statistics:")
        print(f"   Total found:    {stats.get('total_found', 0)}")
        print(f"   Crawled:        {stats.get('total_crawled', 0)}")
        print(f"   Failed:         {stats.get('total_failed', 0)}")
        print(f"   Trusted:        {stats.get('trusted_sources', 0)}")
        print(f"   By source:      {stats.get('by_source', {})}")
        
        # Print first 3 results
        for i, result in enumerate(data['results'][:3], 1):
            print_result(result, i)
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

def example_async_search():
    """Example: Asynchronous search (poll for results)"""
    print("\n" + "="*80)
    print("🔍 Example 2: Asynchronous Search")
    print("="*80)
    
    payload = {
        "query": "AI trong giáo dục Việt Nam",
        "max_results": 50,
        "include_sources": ["all"],
        "languages": ["vi", "en"],
        "deep_crawl": True  # Deep crawl mode
    }
    
    print(f"\n📤 Starting async search: {payload['query']}")
    print(f"   Max results: {payload['max_results']}")
    print(f"   Deep crawl: {payload['deep_crawl']}")
    
    # Start search
    response = requests.post(f"{API_BASE_URL}/search/async", json=payload)
    
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return
    
    data = response.json()
    request_id = data['request_id']
    estimated_time = data.get('estimated_time_seconds', 0)
    
    print(f"\n✅ Search started!")
    print(f"   Request ID: {request_id}")
    print(f"   Estimated time: ~{estimated_time}s")
    
    # Poll for results
    print("\n⏳ Waiting for results...")
    start_time = time.time()
    poll_count = 0
    
    while True:
        poll_count += 1
        time.sleep(5)  # Wait 5 seconds between polls
        
        result_response = requests.get(f"{API_BASE_URL}/search/result/{request_id}")
        
        if result_response.status_code != 200:
            print(f"❌ Error getting results: {result_response.status_code}")
            break
        
        result_data = result_response.json()
        status = result_data.get('status')
        
        if status == 'completed':
            elapsed = time.time() - start_time
            print(f"\n✅ Completed in {elapsed:.2f}s (polled {poll_count} times)")
            
            results = result_data.get('results', [])
            print(f"📊 Found {len(results)} results")
            
            # Print stats
            stats = result_data.get('stats', {})
            print(f"\n📈 Statistics:")
            print(f"   Total found:    {stats.get('total_found', 0)}")
            print(f"   Crawled:        {stats.get('total_crawled', 0)}")
            print(f"   Failed:         {stats.get('total_failed', 0)}")
            print(f"   Trusted:        {stats.get('trusted_sources', 0)}")
            print(f"   Processing:     {stats.get('processing_time_seconds', 0):.2f}s")
            
            by_source = stats.get('by_source', {})
            if by_source:
                print(f"\n📚 Results by source:")
                for source, count in sorted(by_source.items(), key=lambda x: x[1], reverse=True):
                    print(f"   {source:12} {count:3d} results")
            
            # Print first 5 results
            print(f"\n📄 Top {min(5, len(results))} Results:")
            for i, result in enumerate(results[:5], 1):
                print_result(result, i)
            
            break
        
        elif status == 'failed':
            print(f"❌ Search failed: {result_data.get('error_message')}")
            break
        
        else:
            print(f"⏳ Status: {status} (elapsed: {time.time() - start_time:.0f}s)")

def example_targeted_search():
    """Example: Targeted search for specific sources"""
    print("\n" + "="*80)
    print("🔍 Example 3: News & Government Sources Only")
    print("="*80)
    
    payload = {
        "query": "climate change policy 2025",
        "max_results": 30,
        "include_sources": ["news", "government"],
        "languages": ["en"],
        "deep_crawl": True
    }
    
    print(f"\n📤 Searching: {payload['query']}")
    print(f"   Sources: {', '.join(payload['include_sources'])}")
    print(f"   Looking for trusted sources only...")
    
    response = requests.post(f"{API_BASE_URL}/search", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        
        print(f"\n✅ Found {len(results)} results")
        
        # Count trusted vs untrusted
        trusted = [r for r in results if r['url_trust']]
        print(f"   ✅ Trusted sources: {len(trusted)}")
        print(f"   ⚠️  Other sources:  {len(results) - len(trusted)}")
        
        # Print top trusted results
        print(f"\n📰 Top Trusted Results:")
        for i, result in enumerate(trusted[:3], 1):
            print_result(result, i)
    else:
        print(f"❌ Error: {response.status_code}")

def main():
    """Run all examples"""
    print("\n" + "🌟"*40)
    print("Multi-Source Search API - Usage Examples")
    print("🌟"*40)
    
    # Check if API is running
    try:
        health = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if health.status_code != 200:
            print(f"\n❌ API is not healthy. Status: {health.status_code}")
            print("   Please start the API first: python start_api.py")
            return
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Cannot connect to API at {API_BASE_URL}")
        print("   Please start the API first: python start_api.py")
        return
    
    print(f"\n✅ API is running at {API_BASE_URL}")
    
    # Run examples
    choice = input("\nWhich example to run?\n  1. Sync search (fast)\n  2. Async search (deep crawl)\n  3. Trusted sources only\n  4. All examples\nChoice (1-4): ")
    
    if choice == "1":
        example_sync_search()
    elif choice == "2":
        example_async_search()
    elif choice == "3":
        example_targeted_search()
    elif choice == "4":
        example_sync_search()
        example_async_search()
        example_targeted_search()
    else:
        print("Invalid choice")
    
    print("\n" + "="*80)
    print("✨ Examples completed!")
    print("="*80)
    print(f"\n📚 See full docs at: {API_BASE_URL}/docs")

if __name__ == "__main__":
    main()
