#!/usr/bin/env python3
"""
Quick Start Script for Multi-Source Search API
Run this script to start the search API server
"""

import sys
import os
from pathlib import Path

# Add parent directory (trustme_crawl4ai) to Python path để import crawl4ai
parent_dir = str(Path(__file__).parent.parent.absolute())
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Add current directory to path
current_dir = str(Path(__file__).parent.absolute())
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def check_dependencies():
    """Check if required packages are installed"""
    required = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'aiohttp',
        'crawl4ai',
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("❌ Missing dependencies:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\n💡 Install with:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    print("✅ All dependencies installed")
    return True

def main():
    """Start the API server"""
    print("=" * 60)
    print("🔍 Multi-Source Search API")
    print("=" * 60)
    
    if not check_dependencies():
        sys.exit(1)
    
    print("\n🚀 Starting server...")
    print("📍 URL: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("\n⏸️  Press Ctrl+C to stop\n")
    
    import uvicorn
    uvicorn.run(
        "simple_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
