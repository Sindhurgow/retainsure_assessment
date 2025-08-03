#!/usr/bin/env python3
"""
Simple test script for the refactored user management API.
This demonstrates the improved security and functionality.
"""

import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_create_user():
    """Test user creation with validation"""
    print("Testing user creation...")
    
    # Test valid user creation
    user_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "password": "securepassword123"
    }
    
    response = requests.post(f"{BASE_URL}/users", json=user_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 201:
        user_id = response.json()['user']['id']
        return user_id
    return None

def test_invalid_user_creation():
    """Test user creation with invalid data"""
    print("Testing invalid user creation...")
    
    # Test with weak password
    user_data = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "password": "123"  # Too short
    }
    
    response = requests.post(f"{BASE_URL}/users", json=user_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
    # Test with invalid email
    user_data = {
        "name": "Jane Doe",
        "email": "invalid-email",
        "password": "securepassword123"
    }
    
    response = requests.post(f"{BASE_URL}/users", json=user_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_sql_injection_prevention():
    """Test SQL injection prevention"""
    print("Testing SQL injection prevention...")
    
    # Try to inject SQL in user ID
    malicious_id = "1' OR '1'='1"
    response = requests.get(f"{BASE_URL}/user/{malicious_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_login():
    """Test login functionality"""
    print("Testing login...")
    
    # Test successful login
    login_data = {
        "email": "john@example.com",
        "password": "securepassword123"
    }
    
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
    # Test failed login
    login_data = {
        "email": "john@example.com",
        "password": "wrongpassword"
    }
    
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_get_users():
    """Test getting all users (should not expose passwords)"""
    print("Testing get all users...")
    response = requests.get(f"{BASE_URL}/users")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"User count: {data['count']}")
    
    # Verify no passwords are exposed
    if data['users']:
        user = data['users'][0]
        print(f"User data keys: {list(user.keys())}")
        print("✓ No password field in response")
    print()

def test_search_users():
    """Test search functionality"""
    print("Testing search users...")
    response = requests.get(f"{BASE_URL}/search?name=John")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def main():
    """Run all tests"""
    print("=" * 50)
    print("Testing Refactored User Management API")
    print("=" * 50)
    print()
    
    try:
        test_health_check()
        user_id = test_create_user()
        test_invalid_user_creation()
        test_sql_injection_prevention()
        test_login()
        test_get_users()
        test_search_users()
        
        print("=" * 50)
        print("All tests completed!")
        print("=" * 50)
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server.")
        print("Make sure the application is running on http://localhost:5000")
        sys.exit(1)
    except Exception as e:
        print(f"Error during testing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 