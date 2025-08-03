#!/usr/bin/env python3
"""
Demo script for URL Shortener service
This script demonstrates the core functionality of the URL shortener
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def demo_health_check():
    """Demo health check endpoints"""
    print("=" * 50)
    print("Testing Health Check Endpoints")
    print("=" * 50)
    
    # Test basic health check
    response = requests.get(f"{BASE_URL}/")
    print(f"Basic health check: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test API health check
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"API health check: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def demo_url_shortening():
    """Demo URL shortening functionality"""
    print("=" * 50)
    print("Testing URL Shortening")
    print("=" * 50)
    
    # Test URLs to shorten
    test_urls = [
        "https://www.google.com",
        "https://www.github.com",
        "https://www.example.com/very/long/url/that/needs/shortening",
        "http://localhost:3000"
    ]
    
    created_urls = []
    
    for i, url in enumerate(test_urls, 1):
        print(f"Shortening URL {i}: {url}")
        
        response = requests.post(
            f"{BASE_URL}/api/shorten",
            json={"url": url},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Created: {data['short_code']} -> {data['original_url']}")
            created_urls.append(data)
        else:
            print(f"❌ Failed: {response.status_code} - {response.json()}")
        
        print()
    
    return created_urls

def demo_redirects(created_urls):
    """Demo redirect functionality"""
    print("=" * 50)
    print("Testing URL Redirects")
    print("=" * 50)
    
    for url_data in created_urls:
        short_code = url_data['short_code']
        original_url = url_data['original_url']
        
        print(f"Testing redirect: {short_code} -> {original_url}")
        
        # Test redirect (without following it)
        response = requests.get(
            f"{BASE_URL}/{short_code}",
            allow_redirects=False
        )
        
        if response.status_code == 302:
            print(f"✅ Redirect successful: {response.headers.get('Location')}")
        else:
            print(f"❌ Redirect failed: {response.status_code}")
        
        print()

def demo_analytics(created_urls):
    """Demo analytics functionality"""
    print("=" * 50)
    print("Testing Analytics")
    print("=" * 50)
    
    for url_data in created_urls:
        short_code = url_data['short_code']
        
        print(f"Getting stats for: {short_code}")
        
        # Get initial stats
        response = requests.get(f"{BASE_URL}/api/stats/{short_code}")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Initial stats: {stats['click_count']} clicks")
            
            # Visit the URL to increment click count
            print(f"Visiting URL to increment click count...")
            requests.get(f"{BASE_URL}/{short_code}", allow_redirects=False)
            
            # Get updated stats
            response = requests.get(f"{BASE_URL}/api/stats/{short_code}")
            if response.status_code == 200:
                updated_stats = response.json()
                print(f"✅ Updated stats: {updated_stats['click_count']} clicks")
        else:
            print(f"❌ Failed to get stats: {response.status_code}")
        
        print()

def demo_error_handling():
    """Demo error handling"""
    print("=" * 50)
    print("Testing Error Handling")
    print("=" * 50)
    
    # Test invalid URL
    print("Testing invalid URL...")
    response = requests.post(
        f"{BASE_URL}/api/shorten",
        json={"url": "not-a-valid-url"},
        headers={"Content-Type": "application/json"}
    )
    print(f"Invalid URL response: {response.status_code} - {response.json()}")
    
    # Test missing URL field
    print("Testing missing URL field...")
    response = requests.post(
        f"{BASE_URL}/api/shorten",
        json={},
        headers={"Content-Type": "application/json"}
    )
    print(f"Missing URL response: {response.status_code} - {response.json()}")
    
    # Test non-existent short code
    print("Testing non-existent short code...")
    response = requests.get(f"{BASE_URL}/api/stats/nonexistent")
    print(f"Non-existent code response: {response.status_code} - {response.json()}")
    
    # Test invalid short code format
    print("Testing invalid short code format...")
    response = requests.get(f"{BASE_URL}/api/stats/invalid")
    print(f"Invalid format response: {response.status_code} - {response.json()}")
    
    print()

def demo_concurrent_requests():
    """Demo concurrent request handling"""
    print("=" * 50)
    print("Testing Concurrent Requests")
    print("=" * 50)
    
    import threading
    
    results = []
    
    def create_url(i):
        url = f"https://www.example{i}.com"
        response = requests.post(
            f"{BASE_URL}/api/shorten",
            json={"url": url},
            headers={"Content-Type": "application/json"}
        )
        results.append({
            "thread": i,
            "status": response.status_code,
            "success": response.status_code == 201
        })
    
    # Create multiple threads
    threads = []
    for i in range(5):
        thread = threading.Thread(target=create_url, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Report results
    successful = sum(1 for r in results if r['success'])
    print(f"Concurrent requests: {len(results)} total, {successful} successful")
    
    for result in results:
        status = "✅" if result['success'] else "❌"
        print(f"{status} Thread {result['thread']}: {result['status']}")
    
    print()

def main():
    """Run the complete demo"""
    print("🚀 URL Shortener Service Demo")
    print("Make sure the service is running on http://localhost:5000")
    print()
    
    try:
        # Test health checks
        demo_health_check()
        
        # Test URL shortening
        created_urls = demo_url_shortening()
        
        if created_urls:
            # Test redirects
            demo_redirects(created_urls)
            
            # Test analytics
            demo_analytics(created_urls)
        
        # Test error handling
        demo_error_handling()
        
        # Test concurrent requests
        demo_concurrent_requests()
        
        print("=" * 50)
        print("🎉 Demo completed successfully!")
        print("=" * 50)
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the server.")
        print("Make sure the URL shortener service is running on http://localhost:5000")
        print("Run: python app/main.py")
    except Exception as e:
        print(f"❌ Error during demo: {e}")

if __name__ == "__main__":
    main() 