import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.core.security import hash_password
from app.config import settings

async def seed_admin():
    async with AsyncSessionLocal() as db:
        admin_email = settings.ADMIN_EMAIL
        result = await db.execute(select(User).where(User.email == admin_email))
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"Creating admin user: {admin_email}")
            # hash_password is synchronous in passlib usually
            hashed = hash_password(settings.ADMIN_PASSWORD)
            user = User(email=admin_email, hashed_password=hashed, role="admin")
            db.add(user)
            await db.commit()
            print("Admin created successfully.")
        else:
            user.role = "admin"
            user.hashed_password = hash_password(settings.ADMIN_PASSWORD)
            await db.commit()
            print("Existing user updated to admin role with new password.")

if __name__ == "__main__":
    asyncio.run(seed_admin())
