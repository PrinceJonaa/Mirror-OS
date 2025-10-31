#!/usr/bin/env python3.11
"""
Run diagnostics on multiple datasets from tools/relational_math/data
and load them into the dashboard database via API.
"""
import asyncio
import aiohttp
import json
from pathlib import Path

# API endpoint
API_BASE = "http://localhost:8000"

# Define datasets to test
DATASETS = [
    {
        "name": "Discipline Data (Clean)",
        "path": "/Users/princejona/a1/tools/relational_math/data/discipline_data_clean.csv",
        "type": "tabular",
        "description": "School discipline metrics (53k rows, 7 columns)"
    },
    {
        "name": "Lifestyle Combined",
        "path": "/Users/princejona/a1/tools/relational_math/data/lifestyle_combined.csv",
        "type": "tabular",
        "description": "Health and lifestyle metrics (20k rows, ~50 columns)"
    },
    {
        "name": "Credit Card Fraud",
        "path": "/Users/princejona/a1/tools/relational_math/data/creditcard.csv",
        "type": "tabular",
        "description": "Credit card transaction data (285k rows)"
    },
    {
        "name": "GDP Data",
        "path": "/Users/princejona/a1/tools/relational_math/data/gdp_data_clean.csv",
        "type": "tabular",
        "description": "World GDP data (182 rows)"
    },
    {
        "name": "Final Data",
        "path": "/Users/princejona/a1/tools/relational_math/data/Final_data.csv",
        "type": "tabular",
        "description": "Final dataset (20k rows)"
    }
]

async def run_all_diagnostics():
    """Run diagnostics on all datasets via API."""
    print("=" * 80)
    print("Running Truth ↔ Distortion Diagnostics on Multiple Datasets")
    print("=" * 80)
    print()
    
    results = []
    
    async with aiohttp.ClientSession() as session:
        for i, dataset in enumerate(DATASETS, 1):
            print(f"\n[{i}/{len(DATASETS)}] Processing: {dataset['name']}")
            print(f"  File: {dataset['path']}")
            print(f"  Description: {dataset['description']}")
            print("-" * 80)
            
            # Check if file exists
            if not Path(dataset['path']).exists():
                print(f"  ❌ File not found: {dataset['path']}")
                results.append({
                    "name": dataset['name'],
                    "status": "FILE_NOT_FOUND",
                    "error": f"File not found: {dataset['path']}"
                })
                continue
            
            try:
                # Create diagnostic run via API
                payload = {
                    "name": dataset['name'],
                    "description": dataset['description'],
                    "data_path": dataset['path'],
                    "data_type": dataset['type'],
                    "corr_method": "spearman",
                    "adj_threshold": 0.3,
                    "compute_null": True,
                    "n_permutations": 1000,
                    "use_louvain": True,
                    "skip_visuals": False,  # Generate full visualizations including adjacency matrix
                    "seed": 42
                }
                
                async with session.post(f"{API_BASE}/api/runs", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"  ✅ Success! Run ID: {result['id']}")
                        print(f"  Status: {result['status']}")
                        results.append({
                            "name": dataset['name'],
                            "status": "SUCCESS",
                            "run_id": result['id']
                        })
                    else:
                        error_text = await response.text()
                        print(f"  ❌ API Error: {response.status}")
                        print(f"  {error_text}")
                        results.append({
                            "name": dataset['name'],
                            "status": "API_ERROR",
                            "error": f"Status {response.status}: {error_text}"
                        })
                
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
                results.append({
                    "name": dataset['name'],
                    "status": "ERROR",
                    "error": str(e)
                })
    
    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    for result in results:
        status_icon = "✅" if result['status'] == "SUCCESS" else "❌"
        print(f"{status_icon} {result['name']}: {result['status']}")
        if result['status'] == "SUCCESS":
            print(f"   Run ID: {result['run_id']}")
        elif 'error' in result:
            print(f"   Error: {result['error']}")
    
    print("\n" + "=" * 80)
    success_count = sum(1 for r in results if r['status'] == "SUCCESS")
    print(f"✅ Successful: {success_count}/{len(DATASETS)}")
    print(f"❌ Failed: {len(DATASETS) - success_count}/{len(DATASETS)}")
    print("=" * 80)
    print("\n🚀 View results at: http://localhost:3000")
    print("📊 API docs at: http://localhost:8000/docs")
    print()

if __name__ == "__main__":
    asyncio.run(run_all_diagnostics())
