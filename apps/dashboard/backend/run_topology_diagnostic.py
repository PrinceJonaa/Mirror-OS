#!/usr/bin/env python3.11
"""
Run a diagnostic with full topology output (adjacency matrix).
"""
import asyncio
import aiohttp
import json

async def run_diagnostic_with_topology():
    """Run diagnostic on GDP data with topology graph enabled."""
    
    payload = {
        "name": "GDP Data - Full Topology",
        "description": "World GDP data with complete topology graph",
        "data_path": "/Users/princejona/a1/tools/relational_math/data/gdp_data_clean.csv",
        "data_type": "tabular",
        "corr_method": "spearman",
        "adj_threshold": 0.3,
        "compute_null": True,
        "n_permutations": 1000,
        "use_louvain": True,
        "skip_visuals": False,  # Generate full visualizations including adjacency matrix
        "seed": 42
    }
    
    print("=" * 80)
    print("Running diagnostic with full topology graph support")
    print("=" * 80)
    print(f"\nDataset: {payload['data_path']}")
    print(f"Name: {payload['name']}")
    print(f"Skip Visuals: {payload['skip_visuals']} (FALSE = generate adjacency matrix)")
    print("\n" + "-" * 80)
    
    async with aiohttp.ClientSession() as session:
        try:
            print("\n📤 Sending request to API...")
            async with session.post("http://localhost:8000/api/runs", json=payload) as response:
                print(f"📥 Response status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    print(f"\n✅ Success!")
                    print(f"Run ID: {result['id']}")
                    print(f"Status: {result['status']}")
                    
                    # Wait for completion
                    print("\n⏳ Waiting for diagnostic to complete...")
                    run_id = result['id']
                    
                    for i in range(60):  # Wait up to 60 seconds
                        await asyncio.sleep(1)
                        async with session.get(f"http://localhost:8000/api/runs/{run_id}") as check_response:
                            if check_response.status == 200:
                                run_status = await check_response.json()
                                status = run_status.get('status')
                                
                                if status == 'completed':
                                    print(f"\n✅ Diagnostic completed!")
                                    
                                    # Check for topology data
                                    async with session.get(f"http://localhost:8000/api/runs/{run_id}/topology-graph") as topo_response:
                                        if topo_response.status == 200:
                                            topo_data = await topo_response.json()
                                            print(f"\n🎉 Topology graph data available!")
                                            print(f"   Nodes: {topo_data.get('metadata', {}).get('node_count', 'N/A')}")
                                            print(f"   Links: {topo_data.get('metadata', {}).get('link_count', 'N/A')}")
                                            print(f"   Communities: {topo_data.get('metadata', {}).get('community_count', 'N/A')}")
                                        else:
                                            error_text = await topo_response.text()
                                            print(f"\n⚠️ No topology data available")
                                            print(f"   Status: {topo_response.status}")
                                            print(f"   Error: {error_text}")
                                    
                                    print(f"\n🔗 View in dashboard:")
                                    print(f"   http://localhost:3000/runs/{run_id}")
                                    return result
                                elif status == 'failed':
                                    print(f"\n❌ Diagnostic failed!")
                                    if 'error' in run_status:
                                        print(f"   Error: {run_status['error']}")
                                    return None
                                else:
                                    print(f"   Status: {status} (waiting... {i+1}s)", end='\r')
                    
                    print(f"\n⏱️ Timeout waiting for completion")
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
    result = asyncio.run(run_diagnostic_with_topology())
    
    if result:
        print("\n" + "=" * 80)
        print("SUCCESS - Diagnostic run created")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("FAILED - Could not create diagnostic run")
        print("=" * 80)
