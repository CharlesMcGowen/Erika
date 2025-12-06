#!/usr/bin/env python3
"""
Erika Plugin API Test Script
============================
Tests the plugin registration and Erika API endpoints.
"""

import requests
import json
import sys
from typing import Dict, Any

GATEWAY_URL = "http://localhost:8082"
ERIKA_PLUGIN_NAME = "erika"

def test_gateway_health():
    """Test 1: Gateway health check"""
    print("\n" + "="*60)
    print("TEST 1: Gateway Health Check")
    print("="*60)
    try:
        response = requests.get(f"{GATEWAY_URL}/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_plugin_registration():
    """Test 2: Register Erika plugin"""
    print("\n" + "="*60)
    print("TEST 2: Plugin Registration")
    print("="*60)
    
    registration_data = {
        "plugin_name": ERIKA_PLUGIN_NAME,
        "version": "1.0.0",
        "description": "Erika Email Assistant - AI-powered email management and analysis",
        "author": "Living Archive team",
        "endpoints": [
            "/api/erika/health",
            "/api/erika/emails",
            "/api/erika/emails/{email_id}",
            "/api/erika/emails/analyze",
            "/api/erika/gmail/connect",
            "/api/erika/gmail/status",
            "/api/erika/gmail/disconnect",
            "/api/erika/stats"
        ],
        "plugin_url": None,
        "metadata": {
            "type": "email_assistant",
            "capabilities": [
                "email_reading",
                "email_analysis",
                "phishing_detection",
                "gmail_oauth"
            ]
        }
    }
    
    try:
        response = requests.post(
            f"{GATEWAY_URL}/api/plugins/register",
            json=registration_data,
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_list_plugins():
    """Test 3: List all registered plugins"""
    print("\n" + "="*60)
    print("TEST 3: List Plugins")
    print("="*60)
    try:
        response = requests.get(f"{GATEWAY_URL}/api/plugins/list", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_get_plugin_info():
    """Test 4: Get Erika plugin info"""
    print("\n" + "="*60)
    print("TEST 4: Get Plugin Info")
    print("="*60)
    try:
        response = requests.get(f"{GATEWAY_URL}/api/plugins/{ERIKA_PLUGIN_NAME}", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_erika_health():
    """Test 5: Erika health endpoint (if router included)"""
    print("\n" + "="*60)
    print("TEST 5: Erika Health Endpoint")
    print("="*60)
    try:
        response = requests.get(f"{GATEWAY_URL}/api/erika/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"⚠️  Note: {e}")
        print("   This is expected if Erika router is not included in Gateway")
        return False

def test_erika_gmail_status():
    """Test 6: Erika Gmail status (if router included)"""
    print("\n" + "="*60)
    print("TEST 6: Erika Gmail Status")
    print("="*60)
    try:
        response = requests.get(f"{GATEWAY_URL}/api/erika/gmail/status", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"⚠️  Note: {e}")
        print("   This is expected if Erika router is not included in Gateway")
        return False

def test_erika_stats():
    """Test 7: Erika stats (if router included)"""
    print("\n" + "="*60)
    print("TEST 7: Erika Stats")
    print("="*60)
    try:
        response = requests.get(f"{GATEWAY_URL}/api/erika/stats", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"⚠️  Note: {e}")
        print("   This is expected if Erika router is not included in Gateway")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("ERIKA PLUGIN API TEST SUITE")
    print("="*60)
    print(f"Gateway URL: {GATEWAY_URL}")
    print(f"Plugin Name: {ERIKA_PLUGIN_NAME}")
    
    results = []
    
    # Test gateway is running
    if not test_gateway_health():
        print("\n❌ Gateway is not running or not accessible!")
        print("   Please start EgoLlama Gateway first:")
        print("   cd /mnt/webapps-nvme/EgoLlama")
        print("   python unified_llama_gateway.py")
        sys.exit(1)
    
    # Test plugin registration
    results.append(("Plugin Registration", test_plugin_registration()))
    
    # Test plugin listing
    results.append(("List Plugins", test_list_plugins()))
    
    # Test plugin info
    results.append(("Get Plugin Info", test_get_plugin_info()))
    
    # Test Erika endpoints (may fail if router not included)
    results.append(("Erika Health", test_erika_health()))
    results.append(("Erika Gmail Status", test_erika_gmail_status()))
    results.append(("Erika Stats", test_erika_stats()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    elif passed >= 3:  # At least registration and listing work
        print("\n⚠️  Some tests passed. Erika router may need to be included in Gateway.")
    else:
        print("\n❌ Most tests failed. Check gateway connection and plugin registration.")

if __name__ == "__main__":
    main()

