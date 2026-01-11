import asyncio
from sqlalchemy import select
from src.storage_indexing.database import init_db, get_db
from src.storage_indexing.models import User, Tenant

async def check_db():
    init_db()
    async for db in get_db():
        # Check tenants
        tenants_result = await db.execute(select(Tenant))
        tenants = tenants_result.scalars().all()
        print(f"Tenants: {[ (t.tenant_id, t.name) for t in tenants]}")
        
        # Check users
        users_result = await db.execute(select(User))
        users = users_result.scalars().all()
        print(f"Users: {[ (u.user_id, u.email) for u in users]}")
        
        if not tenants:
            print("No tenants found! This might cause issues if tenant_id=1 is used.")
        if not users:
            print("No users found! This might cause ForeignKeyViolation if uploaded_by is set.")

if __name__ == "__main__":
    asyncio.run(check_db())
