"""
Seed local development database with test data.

Usage:
    python scripts/seed-local-db.py

This script creates:
- A test user (test@example.com / password123)
- A sample project associated with the test user
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import AsyncSessionLocal
from app.models.database import User, Project, ProjectStatus
from app.services.auth import hash_password


async def seed_database():
    """Seed database with test data."""
    print("🌱 Seeding local database...")

    async with AsyncSessionLocal() as session:
        try:
            # Create test user
            test_user = User(
                email="test@example.com",
                full_name="Test User",
                hashed_password=hash_password("password123"),
                is_active=True,
            )
            session.add(test_user)
            await session.flush()  # Flush to get the user ID

            # Create test project
            test_project = Project(
                name="Test Project",
                client_name="Test Client",
                property_address="123 Test St, Test City, TS 12345",
                status=ProjectStatus.DRAFT,
                user_id=test_user.id,
            )
            session.add(test_project)

            await session.commit()

            print("✅ Database seeded successfully!")
            print()
            print("Test User:")
            print(f"  Email: {test_user.email}")
            print(f"  Password: password123")
            print(f"  ID: {test_user.id}")
            print()
            print("Test Project:")
            print(f"  Name: {test_project.name}")
            print(f"  Client: {test_project.client_name}")
            print(f"  ID: {test_project.id}")
            print()
            print("You can now login to the application with these credentials.")

        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding database: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed_database())
