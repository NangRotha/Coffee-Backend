#!/usr/bin/env python3
"""
Test simple login endpoint
"""
import requests

# Test login with different formats
login_data = {
    "username": "admin@coffee.com",
    "password": "admin123"
}

# Try JSON format
print("Testing JSON format...")
try:
    response = requests.post(
        "http://localhost:8000/api/v1/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Try form data format
print("\nTesting form data format...")
try:
    response = requests.post(
        "http://localhost:8000/api/v1/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Try with URL encoded
print("\nTesting URL encoded format...")
try:
    import urllib.parse
    encoded_data = urllib.parse.urlencode(login_data)
    response = requests.post(
        "http://localhost:8000/api/v1/auth/login",
        data=encoded_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
