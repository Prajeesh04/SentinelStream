"""Seed the database with initial data: admin user, test user, and fraud rules."""
import asyncio
import sys
import os
from sqlalchemy import select

# Add project root to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.fraud_rule import FraudRule
from app.core.security import hash_password


async def seed():
    async with AsyncSessionLocal() as db:
        # Create admin user
        admin_email = 'admin@sentinelstream.com'
        result = await db.execute(select(User).filter(User.email == admin_email))
        if not result.scalars().first():
            admin = User(
                email=admin_email,
                hashed_password=hash_password('admin123'),
                role='admin',
            )
            db.add(admin)

        # Create test user
        user_email = 'test@bank.com'
        result = await db.execute(select(User).filter(User.email == user_email))
        if not result.scalars().first():
            user = User(
                email=user_email,
                hashed_password=hash_password('password123'),
                home_lat=37.7749,
                home_lng=-122.4194,
            )
            db.add(user)

        # Add default fraud rules
        rules = [
            FraudRule(
                name='high_amount',
                field_name='amount',
                operator='>',
                threshold_value='5000',
                action='DECLINE',
                priority=10,
            ),
            FraudRule(
                name='crypto_merchant',
                field_name='merchant_category',
                operator='=',
                threshold_value='cryptocurrency',
                action='FLAG',
                priority=8,
            ),
            FraudRule(
                name='gambling',
                field_name='merchant_category',
                operator='=',
                threshold_value='gambling',
                action='FLAG',
                priority=7,
            ),
        ]
        for r in rules:
            result = await db.execute(select(FraudRule).filter(FraudRule.name == r.name))
            if not result.scalars().first():
                db.add(r)

        await db.commit()
        print('Seeded: admin user, test user, 3 fraud rules')


if __name__ == '__main__':
    asyncio.run(seed())
