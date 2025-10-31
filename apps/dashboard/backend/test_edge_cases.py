#!/usr/bin/env python3
"""
Edge Case Testing for Phase 4 & 5
Tests various edge cases and boundary conditions
"""
import asyncio
import asyncpg
import json
from datetime import datetime

async def test_edge_cases():
    """Test edge cases in data handling"""
    db_url = 'postgresql://dashboard_user:password@localhost:5432/dashboard_db'
    
    try:
        conn = await asyncpg.connect(db_url)
        print("✓ Database connection successful\n")
        
        # Test 1: Empty result sets
        print("=== Test 1: Empty Result Sets ===")
        empty_runs = await conn.fetch('''
            SELECT * FROM diagnostic_runs WHERE status = 'nonexistent_status'
        ''')
        print(f"✓ Empty runs query returns: {len(empty_runs)} results")
        
        # Test 2: NULL values in metrics
        print("\n=== Test 2: NULL Values in Metrics ===")
        null_metrics = await conn.fetch('''
            SELECT 
                cm.collapse_ratio,
                rm.rfi,
                rm.modularity_q,
                rm.homophily_h
            FROM collapse_metrics cm
            FULL OUTER JOIN rfi_metrics rm ON cm.run_id = rm.run_id
            LIMIT 5
        ''')
        for m in null_metrics:
            has_nulls = any(v is None for v in m.values())
            print(f"  Row: collapse={m['collapse_ratio']}, rfi={m['rfi']}, has_nulls={has_nulls}")
        
        # Test 3: Single run scenario
        print("\n=== Test 3: Single Run Scenario ===")
        single_run = await conn.fetch('''
            SELECT 
                dr.id,
                cm.collapse_ratio,
                rm.rfi
            FROM diagnostic_runs dr
            JOIN collapse_metrics cm ON dr.id = cm.run_id
            JOIN rfi_metrics rm ON dr.id = rm.run_id
            LIMIT 1
        ''')
        if single_run:
            print(f"✓ Single run test data available: {len(single_run)} run(s)")
            print(f"  collapse_ratio range: [{single_run[0]['collapse_ratio']}]")
            print(f"  rfi range: [{single_run[0]['rfi']}]")
        else:
            print("  ⚠️  No runs available for single run test")
        
        # Test 4: Extreme values
        print("\n=== Test 4: Extreme Values ===")
        extreme = await conn.fetch('''
            SELECT 
                MIN(cm.collapse_ratio) as min_collapse,
                MAX(cm.collapse_ratio) as max_collapse,
                MIN(rm.rfi) as min_rfi,
                MAX(rm.rfi) as max_rfi,
                MIN(rm.modularity_q) as min_mod,
                MAX(rm.modularity_q) as max_mod
            FROM collapse_metrics cm
            JOIN rfi_metrics rm ON cm.run_id = rm.run_id
        ''')
        if extreme:
            e = extreme[0]
            print(f"  Collapse ratio: [{e['min_collapse']:.4f}, {e['max_collapse']:.4f}]")
            print(f"  RFI: [{e['min_rfi']:.4f}, {e['max_rfi']:.4f}]")
            print(f"  Modularity: [{e['min_mod']}, {e['max_mod']}]")
        
        # Test 5: JSON parsing edge cases
        print("\n=== Test 5: JSON Parsing ===")
        results = await conn.fetch('''
            SELECT run_id, results, file_paths 
            FROM diagnostic_results 
            LIMIT 3
        ''')
        for r in results:
            try:
                # Test if results is already parsed or needs parsing
                if isinstance(r['results'], str):
                    parsed = json.loads(r['results'])
                    print(f"  ✓ Run {r['run_id']}: JSON string parsed successfully")
                elif isinstance(r['results'], dict):
                    print(f"  ✓ Run {r['run_id']}: Already parsed as dict")
                else:
                    print(f"  ⚠️  Run {r['run_id']}: Unexpected type {type(r['results'])}")
            except json.JSONDecodeError as e:
                print(f"  ✗ Run {r['run_id']}: JSON parse error: {e}")
        
        # Test 6: Datetime handling
        print("\n=== Test 6: Datetime Handling ===")
        dates = await conn.fetch('''
            SELECT id, created_at, started_at, completed_at 
            FROM diagnostic_runs 
            LIMIT 3
        ''')
        for d in dates:
            print(f"  Run {d['id']}:")
            for field in ['created_at', 'started_at', 'completed_at']:
                val = d[field]
                if val:
                    if hasattr(val, 'isoformat'):
                        print(f"    {field}: {val.isoformat()} (datetime)")
                    else:
                        print(f"    {field}: {val} (type: {type(val).__name__})")
                else:
                    print(f"    {field}: NULL")
        
        # Test 7: Missing topology data
        print("\n=== Test 7: Missing Topology Data ===")
        topo_check = await conn.fetch('''
            SELECT 
                dr.id,
                dr.status,
                CASE 
                    WHEN dr_res.results::text LIKE '%adjacency%' THEN true 
                    ELSE false 
                END as has_adjacency
            FROM diagnostic_runs dr
            LEFT JOIN diagnostic_results dr_res ON dr.id = dr_res.run_id
            WHERE dr.status = 'completed'
            LIMIT 5
        ''')
        for t in topo_check:
            print(f"  Run {t['id']}: has_adjacency={t['has_adjacency']}")
        
        # Test 8: Division by zero cases
        print("\n=== Test 8: Division by Zero Safety ===")
        stats = await conn.fetch('''
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE status = 'completed') as completed
            FROM diagnostic_runs
        ''')
        total = stats[0]['total']
        completed = stats[0]['completed']
        success_rate = (completed / total * 100) if total > 0 else 0
        print(f"  Total: {total}, Completed: {completed}")
        print(f"  Success rate: {success_rate:.2f}%")
        print(f"  ✓ Division by zero handled correctly")
        
        await conn.close()
        print("\n" + "="*50)
        print("✓ All edge case tests completed successfully!")
        print("="*50)
        
    except Exception as e:
        print(f"\n✗ Edge case test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_edge_cases())
