import pytest
import json
from app.main import app
from app.models import db

@pytest.fixture
def client():
    """Test client fixture"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def clean_db():
    """Clean database before each test"""
    # Clear all URLs before each test
    all_urls = db.get_all_urls()
    for url in all_urls:
        db.delete_url(url['short_code'])
    yield
    # Clean up after test
    all_urls = db.get_all_urls()
    for url in all_urls:
        db.delete_url(url['short_code'])

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['service'] == 'URL Shortener API'

def test_api_health(client):
    """Test API health endpoint"""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'
    assert data['message'] == 'URL Shortener API is running'

def test_shorten_url_success(client, clean_db):
    """Test successful URL shortening"""
    url_data = {
        "url": "https://www.example.com/very/long/url/that/needs/shortening"
    }
    
    response = client.post('/api/shorten', 
                         data=json.dumps(url_data),
                         content_type='application/json')
    
    assert response.status_code == 201
    data = response.get_json()
    
    # Check response structure
    assert 'short_code' in data
    assert 'original_url' in data
    assert 'short_url' in data
    
    # Check short code format (6 alphanumeric characters)
    assert len(data['short_code']) == 6
    assert data['short_code'].isalnum()
    
    # Check original URL
    assert data['original_url'] == "https://www.example.com/very/long/url/that/needs/shortening"
    
    # Check short URL format
    assert data['short_url'] == f"http://localhost:5000/{data['short_code']}"

def test_shorten_url_missing_url(client):
    """Test URL shortening with missing URL field"""
    url_data = {}
    
    response = client.post('/api/shorten',
                         data=json.dumps(url_data),
                         content_type='application/json')
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'Missing' in data['error']

def test_shorten_url_invalid_url(client):
    """Test URL shortening with invalid URL"""
    url_data = {
        "url": "not-a-valid-url"
    }
    
    response = client.post('/api/shorten',
                         data=json.dumps(url_data),
                         content_type='application/json')
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'Invalid URL format' in data['error']

def test_shorten_url_no_json(client):
    """Test URL shortening without JSON content"""
    response = client.post('/api/shorten')
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_redirect_success(client, clean_db):
    """Test successful redirect"""
    # First, create a short URL
    url_data = {
        "url": "https://www.google.com"
    }
    
    create_response = client.post('/api/shorten',
                                data=json.dumps(url_data),
                                content_type='application/json')
    
    assert create_response.status_code == 201
    short_code = create_response.get_json()['short_code']
    
    # Now test the redirect
    redirect_response = client.get(f'/{short_code}')
    
    # Should redirect to Google
    assert redirect_response.status_code == 302
    assert redirect_response.location == "https://www.google.com"

def test_redirect_nonexistent_code(client):
    """Test redirect with non-existent short code"""
    response = client.get('/nonexistent')
    
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data
    assert 'not found' in data['error'].lower()

def test_redirect_invalid_code_format(client):
    """Test redirect with invalid short code format"""
    response = client.get('/invalid')
    
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data

def test_get_stats_success(client, clean_db):
    """Test getting URL statistics"""
    # First, create a short URL
    url_data = {
        "url": "https://www.github.com"
    }
    
    create_response = client.post('/api/shorten',
                                data=json.dumps(url_data),
                                content_type='application/json')
    
    assert create_response.status_code == 201
    short_code = create_response.get_json()['short_code']
    
    # Get initial stats
    stats_response = client.get(f'/api/stats/{short_code}')
    
    assert stats_response.status_code == 200
    data = stats_response.get_json()
    
    # Check response structure
    assert 'short_code' in data
    assert 'original_url' in data
    assert 'click_count' in data
    assert 'created_at' in data
    
    # Check initial values
    assert data['short_code'] == short_code
    assert data['original_url'] == "https://www.github.com"
    assert data['click_count'] == 0
    
    # Now visit the URL to increment click count
    client.get(f'/{short_code}')
    
    # Get updated stats
    updated_stats_response = client.get(f'/api/stats/{short_code}')
    
    assert updated_stats_response.status_code == 200
    updated_data = updated_stats_response.get_json()
    
    # Check that click count increased
    assert updated_data['click_count'] == 1

def test_get_stats_nonexistent_code(client):
    """Test getting stats for non-existent short code"""
    response = client.get('/api/stats/nonexistent')
    
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data
    assert 'not found' in data['error'].lower()

def test_get_stats_invalid_format(client):
    """Test getting stats with invalid short code format"""
    response = client.get('/api/stats/invalid')
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'Invalid short code format' in data['error']

def test_concurrent_requests(client, clean_db):
    """Test handling of concurrent requests"""
    import threading
    import time
    
    results = []
    
    def create_url():
        url_data = {
            "url": f"https://www.example{i}.com"
        }
        response = client.post('/api/shorten',
                             data=json.dumps(url_data),
                             content_type='application/json')
        results.append(response.status_code)
    
    # Create multiple threads to test concurrency
    threads = []
    for i in range(5):
        thread = threading.Thread(target=create_url)
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # All requests should succeed
    assert all(status == 201 for status in results)
    
    # All short codes should be unique
    all_urls = db.get_all_urls()
    short_codes = [url['short_code'] for url in all_urls]
    assert len(short_codes) == len(set(short_codes))

def test_url_validation(client):
    """Test various URL validation scenarios"""
    valid_urls = [
        "https://www.example.com",
        "http://localhost:3000",
        "https://subdomain.example.co.uk/path?param=value",
        "http://192.168.1.1:8080"
    ]
    
    invalid_urls = [
        "not-a-url",
        "ftp://example.com",  # Only http/https supported
        "https://",  # Missing domain
        "http://.com",  # Invalid domain
        ""
    ]
    
    # Test valid URLs
    for url in valid_urls:
        url_data = {"url": url}
        response = client.post('/api/shorten',
                             data=json.dumps(url_data),
                             content_type='application/json')
        assert response.status_code == 201
    
    # Test invalid URLs
    for url in invalid_urls:
        url_data = {"url": url}
        response = client.post('/api/shorten',
                             data=json.dumps(url_data),
                             content_type='application/json')
        assert response.status_code == 400

def test_error_handling(client):
    """Test error handling for various scenarios"""
    # Test 404 for non-existent endpoint
    response = client.get('/api/nonexistent')
    assert response.status_code == 404
    
    # Test malformed JSON
    response = client.post('/api/shorten',
                          data="invalid json",
                          content_type='application/json')
    assert response.status_code == 400
    
    # Test empty request body
    response = client.post('/api/shorten')
    assert response.status_code == 400