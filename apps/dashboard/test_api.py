#!/usr/bin/env python3
"""
Test script for the Truth-Distortion Dashboard API
"""

import asyncio
import httpx
import json
from pathlib import Path

API_BASE = "http://localhost:8000"

async def test_api():
    """Test the basic API functionality"""

    async with httpx.AsyncClient(base_url=API_BASE) as client:
        print("🧪 Testing Truth-Distortion Dashboard API")
        print("=" * 50)

        # Test health check
        print("\n1. Testing health check...")
        try:
            response = await client.get("/health")
            print(f"   ✅ Health check: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   ❌ Health check failed: {e}")
            return

        # Test creating a run
        print("\n2. Testing run creation...")
        test_data_path = "/Users/princejona/a1/solutions/test_data/test_matrix.csv"

        # Create a simple test CSV if it doesn't exist
        test_file = Path(test_data_path)
        if not test_file.exists():
            print(f"   Creating test data file: {test_data_path}")
            test_file.parent.mkdir(parents=True, exist_ok=True)
            # Create a simple 5x5 correlation matrix
            import numpy as np
            np.random.seed(42)
            data = np.random.randn(5, 5)
            data = (data + data.T) / 2  # Make symmetric
            np.fill_diagonal(data, 1.0)  # Unit diagonal
            data = np.clip(data, -1, 1)  # Clip to valid correlation range

            import pandas as pd
            df = pd.DataFrame(data, columns=[f'feature_{i}' for i in range(5)])
            df.to_csv(test_file, index=False)
            print(f"   Created test matrix with shape {df.shape}")

        run_data = {
            "name": "API Test Run",
            "description": "Testing the FastAPI wrapper around truth_distortion_unified.py",
            "data_path": test_data_path,
            "data_type": "tabular",
            "corr_method": "pearson",
            "adj_threshold": 0.7,
            "skip_visuals": True  # Skip for faster testing
        }

        try:
            response = await client.post("/api/runs", json=run_data)
            if response.status_code == 200:
                run_result = response.json()
                run_id = run_result["id"]
                print(f"   ✅ Run created: {run_id}")
                print(f"   Status: {run_result['status']}")
            else:
                print(f"   ❌ Run creation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return
        except Exception as e:
            print(f"   ❌ Run creation failed: {e}")
            return

        # Test getting run status
        print(f"\n3. Testing run status polling for {run_id}...")
        max_attempts = 30  # 30 seconds timeout
        attempt = 0
        for attempt in range(max_attempts):
            try:
                response = await client.get(f"/api/runs/{run_id}/status")
                if response.status_code == 200:
                    status_data = response.json()
                    status = status_data["status"]
                    print(f"   Attempt {attempt + 1}: Status = {status}")

                    if status == "completed":
                        print("   ✅ Diagnostic completed!")
                        break
                    elif status == "failed":
                        print(f"   ❌ Diagnostic failed: {status_data.get('error', 'Unknown error')}")
                        break
                else:
                    print(f"   ❌ Status check failed: {response.status_code}")
                    break
            except Exception as e:
                print(f"   ❌ Status check failed: {e}")
                break

            await asyncio.sleep(1)

        if attempt == max_attempts - 1:
            print("   ⏰ Timeout waiting for completion")
            return

        # Test getting full run results
        print(f"\n4. Testing full run results retrieval...")
        try:
            response = await client.get(f"/api/runs/{run_id}")
            if response.status_code == 200:
                run_details = response.json()
                print("   ✅ Full run details retrieved")
                print(f"   Run name: {run_details['name']}")
                print(f"   Status: {run_details['status']}")
                print(f"   Completed at: {run_details.get('completed_at', 'N/A')}")

                # Check if results are available
                if 'results' in run_details and run_details['results']:
                    results = run_details['results']
                    print("   📊 Results summary:")
                    print(f"      M_eff: {results['meff']['meff_min']:.3f}")
                    print(f"      Collapse ratio: {results['meff']['collapse_ratio']:.3f}")
                    print(f"      RFI: {results['rfi']['rfi']:.3f}")
                    print(f"      Shape: {results['shape']['shape']}")
                    print(f"      Lattice position: {results['lattice']['lattice_position']}")
                else:
                    print("   ⚠️  Results not yet available in database")
            else:
                print(f"   ❌ Results retrieval failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Results retrieval failed: {e}")

        # Test listing runs
        print(f"\n5. Testing run listing...")
        try:
            response = await client.get("/api/runs")
            if response.status_code == 200:
                runs_list = response.json()
                print(f"   ✅ Retrieved {len(runs_list['runs'])} runs")
                for run in runs_list['runs'][:3]:  # Show first 3
                    print(f"      {run['id'][:8]}... - {run['name']} ({run['status']})")
            else:
                print(f"   ❌ Run listing failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Run listing failed: {e}")

        print("\n🎉 API testing complete!")
        print("\nNext steps:")
        print("1. Check the generated results in results/{run_id}/")
        print("2. Start building the Next.js frontend")
        print("3. Add LiteLLM for AI interpretations")

if __name__ == "__main__":
    asyncio.run(test_api())