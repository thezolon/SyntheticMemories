#!/usr/bin/env python3
"""Basic smoke tests for advanced-memory service."""

import requests
import time
import sys

BASE_URL = "http://localhost:8768"

def test_health():
    """Test /health endpoint."""
    print("Testing /health endpoint...")
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        
        assert data.get("status") in ["healthy", "degraded"], "Invalid status"
        assert "ollama_connected" in data, "Missing ollama_connected"
        assert "memory_count" in data, "Missing memory_count"
        
        print(f"✓ Health check passed: {data}")
        return True
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False

def test_store_recall():
    """Test store and recall cycle."""
    print("\nTesting /store and /recall...")
    try:
        # Store a test memory
        store_data = {
            "content": "Test memory: Python is a programming language",
            "tier": "session",
            "user_id": "test_user",
            "importance": 6
        }
        
        print(f"Storing: {store_data['content']}")
        store_resp = requests.post(f"{BASE_URL}/store", json=store_data, timeout=10)
        store_resp.raise_for_status()
        store_result = store_resp.json()
        
        assert store_result.get("success") == True, "Store failed"
        assert "memory_id" in store_result, "No memory_id returned"
        
        print(f"✓ Stored memory: {store_result['memory_id']}")
        
        # Wait a moment for indexing
        time.sleep(1)
        
        # Recall the memory
        print("Recalling: 'programming language'")
        recall_resp = requests.get(
            f"{BASE_URL}/recall",
            params={"query": "programming language", "limit": 5},
            timeout=10
        )
        recall_resp.raise_for_status()
        recall_result = recall_resp.json()
        
        assert recall_result.get("count", 0) > 0, "No results found"
        assert len(recall_result.get("results", [])) > 0, "Empty results"
        
        # Check if our test memory is in results
        found = any("Python" in r.get("content", "") for r in recall_result["results"])
        assert found, "Test memory not found in recall"
        
        print(f"✓ Recalled {recall_result['count']} memories")
        print(f"  Top result: {recall_result['results'][0]['content'][:80]}...")
        
        return True
    except Exception as e:
        print(f"✗ Store/Recall test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_importance_threshold():
    """Test that low-importance memories are rejected."""
    print("\nTesting importance threshold...")
    try:
        # Try to store a low-importance memory
        low_importance = {
            "content": "okay",
            "tier": "session",
            "importance": 2  # Below default threshold of 5
        }
        
        resp = requests.post(f"{BASE_URL}/store", json=low_importance, timeout=10)
        
        # Should get 400 error for low importance
        if resp.status_code == 400:
            print(f"✓ Low-importance memory correctly rejected: {resp.json().get('detail')}")
            return True
        else:
            print(f"✗ Expected 400 error, got {resp.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Importance threshold test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Advanced Memory Service - Smoke Tests")
    print("=" * 60)
    
    # Wait for service to be ready
    print("\nWaiting for service to be ready...")
    for i in range(10):
        try:
            requests.get(f"{BASE_URL}/health", timeout=2)
            print("✓ Service is ready")
            break
        except:
            if i == 9:
                print("✗ Service not responding after 10 attempts")
                sys.exit(1)
            time.sleep(2)
    
    # Run tests
    tests = [
        test_health,
        test_store_recall,
        test_importance_threshold
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    # Summary
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("✓ All tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
