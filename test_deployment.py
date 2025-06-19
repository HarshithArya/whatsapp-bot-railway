#!/usr/bin/env python3
"""
Test script to verify Railway deployment
Replace YOUR_RAILWAY_URL with your actual Railway URL
"""

import requests
import json

def test_deployment(base_url):
    """Test all endpoints of the deployed bot"""
    
    print(f"Testing deployment at: {base_url}")
    print("=" * 50)
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"✅ Health endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Threads: {data.get('threads_count')}")
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
    
    # Test home endpoint
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"✅ Home endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Message: {data.get('message')}")
            print(f"   Version: {data.get('version')}")
    except Exception as e:
        print(f"❌ Home endpoint failed: {e}")
    
    # Test webhook endpoint (should return 403 without params)
    try:
        response = requests.get(f"{base_url}/webhook", timeout=10)
        print(f"✅ Webhook endpoint: {response.status_code} (expected 403)")
    except Exception as e:
        print(f"❌ Webhook endpoint failed: {e}")
    
    print("=" * 50)
    print("🎉 Deployment test completed!")

if __name__ == "__main__":
    # Replace with your actual Railway URL
    RAILWAY_URL = "https://your-app-name.railway.app"  # Replace this!
    
    if RAILWAY_URL == "https://your-app-name.railway.app":
        print("⚠️  Please update the RAILWAY_URL variable with your actual Railway URL")
        print("Example: https://my-whatsapp-bot.railway.app")
    else:
        test_deployment(RAILWAY_URL) 