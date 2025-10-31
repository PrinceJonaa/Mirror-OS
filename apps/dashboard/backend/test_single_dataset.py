#!/usr/bin/env python3.11
"""
Test a single dataset diagnostic run via API.
"""
import asyncio
import aiohttp
import json

API_BASE = "http://localhost:8000"

async def test_dataset(name: str, path: str, description: str):
    """Test running diagnostic on a single dataset."""
    print("=" * 80)
    print(f"Testing: {name}")
    print(f"Path: {path}")
    print(f"Description: {description}")
    print("=" * 80)
    
    payload = {
        "name": name,
        "description": description,
        "data_path": path,
        "data_type": "tabular",
        "corr_method": "spearman",
        "adj_threshold": 0.3,
        "compute_null": True,
        "n_permutations": 1000,
        "use_louvain": True,
        "skip_visuals": False,  # Generate full visualizations including adjacency matrix
        "seed": 42
    }
    
    print("\n📤 Sending request to API...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"{API_BASE}/api/runs", json=payload) as response:
                print(f"\n📥 Response status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    print(f"\n✅ Success!")
                    print(f"Run ID: {result['id']}")
                    print(f"Status: {result['status']}")
                    print(f"\nFull response:")
                    print(json.dumps(result, indent=2))
                    return result
                else:
                    error_text = await response.text()
                    print(f"\n❌ API Error: {response.status}")
                    print(f"Error details:\n{error_text}")
                    return None
                    
        except Exception as e:
            print(f"\n❌ Exception occurred: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

if __name__ == "__main__":
    # Start with the smallest dataset: GDP data (182 rows)
    result = asyncio.run(test_dataset(
        name="GDP Data (World Bank)",
        path="/Users/princejona/a1/tools/relational_math/data/gdp_data_clean.csv",
        description="World GDP data - 182 rows"
    ))
    
    if result:
        print("\n" + "=" * 80)
        print("🚀 View result at: http://localhost:3000")
        print(f"📊 Direct link: http://localhost:3000/runs/{result['id']}")
        print("=" * 80)
