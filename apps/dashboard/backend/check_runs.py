import asyncio
import asyncpg

async def check():
    conn = await asyncpg.connect('postgresql://dashboard_user:dashboard_pass@localhost:5432/dashboard_db')
    runs = await conn.fetch('SELECT id, name, data_path, status FROM diagnostic_runs ORDER BY created_at DESC LIMIT 10')
    print("\nExisting diagnostic runs:")
    print("-" * 80)
    if not runs:
        print("No diagnostic runs found in database.")
    for r in runs:
        print(f"{r['id']}: {r['name']}")
        print(f"  Data: {r['data_path']}")
        print(f"  Status: {r['status']}")
        print()
    await conn.close()

asyncio.run(check())
