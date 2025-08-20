#!/usr/bin/env python3
"""
Test script for the authentication system
"""
import requests
import json

BASE_URL = "http://localhost:8001"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health check: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_register():
    """Test user registration"""
    user_data = {
        "email": "doctor@hospital.com",
        "full_name": "Dr. John Smith",
        "role": "doctor",
        "password": "password123",
        "is_active": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=user_data)
        print(f"Register: {response.status_code}")
        if response.status_code == 200:
            print(f"User created: {response.json()}")
            return True
        else:
            print(f"Registration failed: {response.text}")
            return False
    except Exception as e:
        print(f"Registration error: {e}")
        return False

def test_login():
    """Test user login"""
    login_data = {
        "email": "doctor@hospital.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
        print(f"Login: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            print(f"Login successful: {token_data}")
            return token_data.get("access_token")
        else:
            print(f"Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def test_protected_endpoint(token):
    """Test accessing protected endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
        print(f"Protected endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"User info: {response.json()}")
            return True
        else:
            print(f"Protected endpoint failed: {response.text}")
            return False
    except Exception as e:
        print(f"Protected endpoint error: {e}")
        return False

def main():
    print("🧪 Testing Authentication System")
    print("=" * 40)
    
    # Test health
    print("\n1. Testing health endpoint...")
    if not test_health():
        print("❌ Service is not running. Please start the patient service first.")
        return
    
    print("✅ Service is running!")
    
    # Test registration
    print("\n2. Testing user registration...")
    if test_register():
        print("✅ User registration successful!")
    else:
        print("⚠️  User might already exist, continuing with login test...")
    
    # Test login
    print("\n3. Testing user login...")
    token = test_login()
    if token:
        print("✅ Login successful!")
        
        # Test protected endpoint
        print("\n4. Testing protected endpoint...")
        if test_protected_endpoint(token):
            print("✅ Protected endpoint access successful!")
        else:
            print("❌ Protected endpoint access failed!")
    else:
        print("❌ Login failed!")
    
    print("\n" + "=" * 40)
    print("🎉 Authentication testing complete!")

if __name__ == "__main__":
    main()
