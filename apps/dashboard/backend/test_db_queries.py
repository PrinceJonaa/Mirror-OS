#!/usr/bin/env python3
"""
Simple script to test Phase 5 backend endpoints
"""
import asyncio
import asyncpg
import json

async def test_database():
    """Test database connection and queries"""
    db_url = 'postgresql://dashboard_user:password@localhost:5432/dashboard_db'
    
    try:
        conn = await asyncpg.connect(db_url)
        print("✓ Database connection successful")
        
        # Test lattice points query
        print("\n=== Testing Lattice Points Query ===")
        points = await conn.fetch('''
            SELECT
                dr.id as run_id,
                cm.collapse_ratio,
                rm.rfi,
                'Unknown' as shape,
                dr.status,
                dr.created_at
            FROM diagnostic_runs dr
            JOIN collapse_metrics cm ON dr.id = cm.run_id
            JOIN rfi_metrics rm ON dr.id = rm.run_id
            WHERE dr.status = 'completed'
            ORDER BY dr.created_at DESC
            LIMIT 5
        ''')
        print(f"✓ Found {len(points)} lattice points")
        for p in points[:3]:
            print(f"  - Run {p['run_id']}: collapse={p['collapse_ratio']:.3f}, rfi={p['rfi']:.3f}")
        
        # Test collapse map query
        print("\n=== Testing Collapse Map Query ===")
        patterns = await conn.fetch('''
            SELECT
                dr.id as run_id,
                cm.collapse_ratio,
                rm.rfi,
                rm.modularity_q,
                rm.homophily_h,
                rm.lambda_2,
                rm.transitivity,
                dr.status
            FROM diagnostic_runs dr
            JOIN collapse_metrics cm ON dr.id = cm.run_id
            JOIN rfi_metrics rm ON dr.id = rm.run_id
            WHERE dr.status = 'completed'
            LIMIT 3
        ''')
        print(f"✓ Found {len(patterns)} collapse patterns")
        for p in patterns[:2]:
            print(f"  - Run {p['run_id']}: modularity_q={p.get('modularity_q', 'N/A')}")
        
        # Test topology data
        print("\n=== Testing Topology Data ===")
        runs = await conn.fetch('''
            SELECT id, status FROM diagnostic_runs 
            WHERE status = 'completed' 
            LIMIT 3
        ''')
        
        for run in runs:
            result = await conn.fetchrow('''
                SELECT results FROM diagnostic_results WHERE run_id = $1
            ''', run['id'])
            
            if result and result['results']:
                data = result['results']
                has_adjacency = 'adjacency_matrix' in str(data) or 'rfi' in str(data)
                print(f"  - Run {run['id']}: has_topology_data={has_adjacency}")
                if has_adjacency and isinstance(data, dict):
                    print(f"    Keys: {list(data.keys())[:5]}")
        
        await conn.close()
        print("\n✓ All database tests passed!")
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_database())
