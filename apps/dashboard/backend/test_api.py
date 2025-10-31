#!/usr/bin/env python3
"""
API Testing Script for Truth Distortion Integration Dashboard
Tests the FastAPI wrapper around truth_distortion_unified.py
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

async def test_api():
    """Test the FastAPI endpoints for the diagnostic dashboard"""

    print("🚀 Starting API Tests for Truth Distortion Integration Dashboard")
    print("=" * 60)

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:

        # Test 1: Health Check
        print("\n1. Testing Health Check Endpoint")
        try:
            response = await client.get("/health")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Health check passed")
            else:
                print(f"   ❌ Health check failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Health check error: {e}")

        # Test 2: Create Diagnostic Run
        print("\n2. Testing Diagnostic Run Creation")
        try:
            # Payload must match DiagnosticRunCreate model in main.py
            run_data = {
                "name": "Test Diagnostic Run",
                "description": "Automated test of the diagnostic wrapper",
                "data_path": "/Users/princejona/a1/tools/relational_math/data/insurance.csv",
                "data_type": "auto",
                "corr_method": "pearson",
                "adj_threshold": 0.7,
                "compute_null": False,
                "n_permutations": 100,
                "use_louvain": False,
                "skip_visuals": True,
                "seed": None
            }

            response = await client.post("/api/runs", json=run_data)
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                run_result = response.json()
                run_id = run_result["id"]  # API returns "id" not "run_id"
                print(f"   ✅ Run created with ID: {run_id}")
                print(f"   Run details: {json.dumps(run_result, indent=2)}")
            else:
                print(f"   ❌ Run creation failed: {response.text}")
                return

        except Exception as e:
            print(f"   ❌ Run creation error: {e}")
            return

        # Test 3: Check Run Status
        print(f"\n3. Testing Run Status Check for ID: {run_id}")
        try:
            # Poll status a few times
            for i in range(5):
                response = await client.get(f"/api/runs/{run_id}/status")
                print(f"   Poll {i+1} - Status: {response.status_code}")

                if response.status_code == 200:
                    status_data = response.json()
                    status = status_data.get("status")
                    print(f"   Current status: {status}")

                    if status == "completed":
                        print("   ✅ Run completed successfully")
                        break
                    elif status == "failed":
                        print(f"   ❌ Run failed: {status_data.get('error')}")
                        break
                    else:
                        print("   ⏳ Run still in progress, waiting...")
                        await asyncio.sleep(2)
                else:
                    print(f"   ❌ Status check failed: {response.text}")
                    break

        except Exception as e:
            print(f"   ❌ Status check error: {e}")

        # Test 4: Get Run Results
        print(f"\n4. Testing Run Results Retrieval for ID: {run_id}")
        try:
            response = await client.get(f"/api/runs/{run_id}/results")
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                results = response.json()
                print("   ✅ Results retrieved successfully")
                print(f"   Results summary: {len(results.get('metrics', []))} metrics, {len(results.get('patterns', []))} patterns")

                # Show a sample of the results
                if results.get("metrics"):
                    print(f"   Sample metric: {results['metrics'][0]}")

            else:
                print(f"   ❌ Results retrieval failed: {response.text}")

        except Exception as e:
            print(f"   ❌ Results retrieval error: {e}")

        # Test 5: List All Runs
        print("\n5. Testing Run Listing")
        try:
            response = await client.get("/api/runs")
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                runs = response.json()
                print(f"   ✅ Retrieved {len(runs)} runs")
                if runs:
                    print(f"   Latest run: {runs[0]}")
            else:
                print(f"   ❌ Run listing failed: {response.text}")

        except Exception as e:
            print(f"   ❌ Run listing error: {e}")

        # Test 6: Get Dashboard Stats
        print("\n6. Testing Dashboard Statistics")
        try:
            response = await client.get("/api/dashboard/stats")
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                stats = response.json()
                print("   ✅ Dashboard stats retrieved")
                print(f"   Stats: {json.dumps(stats, indent=2)}")
            else:
                print(f"   ❌ Stats retrieval failed: {response.text}")

        except Exception as e:
            print(f"   ❌ Stats retrieval error: {e}")

    print("\n" + "=" * 60)
    print("🏁 API Tests Completed")
    print("\nNote: This test assumes the FastAPI server is running on localhost:8000")
    print("To run the server: python3.11 main.py")

if __name__ == "__main__":
    asyncio.run(test_api())