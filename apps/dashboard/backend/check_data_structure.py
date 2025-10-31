#!/usr/bin/env python3
"""Check diagnostic results structure"""
import asyncio
import asyncpg
import json

async def check_results():
    conn = await asyncpg.connect('postgresql://dashboard_user:password@localhost:5432/dashboard_db')
    
    result = await conn.fetchrow('''
        SELECT results FROM diagnostic_results 
        WHERE run_id = '17c13c83-593e-4b7d-b13b-1c8528a4cceb'
    ''')
    
    if result and result['results']:
        data = result['results']
        if isinstance(data, str):
            data = json.loads(data)
        
        print("=== Top-level keys ===")
        print(list(data.keys()) if isinstance(data, dict) else "Not a dict")
        
        if 'rfi' in data:
            print("\n=== RFI keys ===")
            rfi_keys = list(data['rfi'].keys()) if isinstance(data.get('rfi'), dict) else []
            for key in rfi_keys:
                val = data['rfi'][key]
                val_type = type(val).__name__
                if isinstance(val, (list, dict)):
                    print(f"  {key}: {val_type} (len={len(val)})")
                else:
                    print(f"  {key}: {val_type} = {val}")
        
        # Check _files section
        if '_files' in data:
            print("\n=== _files section ===")
            print(data['_files'])
        
        # Look for adjacency or graph data recursively
        print("\n=== Searching for graph/adjacency data ===")
        def search_dict(d, prefix=""):
            if not isinstance(d, dict):
                return
            for k, v in d.items():
                if 'adj' in k.lower() or 'graph' in k.lower() or 'matrix' in k.lower():
                    print(f"Found: {prefix}.{k} = {type(v).__name__}")
                if isinstance(v, dict):
                    search_dict(v, f"{prefix}.{k}")
        
        search_dict(data, "root")
    
    await conn.close()

asyncio.run(check_results())
