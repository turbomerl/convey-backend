"""
Database configuration and session management
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from .config import settings


def is_serverless() -> bool:
    """Detect if running in serverless environment"""
    return any([
        os.getenv("VERCEL"),
        os.getenv("AWS_LAMBDA_FUNCTION_NAME"),
        os.getenv("FUNCTIONS_EXTENSION_VERSION"),  # Azure
    ])


# Create async engine with serverless-optimized settings
engine = create_async_engine(
    settings.get_database_url(),
    echo=settings.database_echo,
    pool_size=1 if is_serverless() else settings.database_pool_size,
    max_overflow=0 if is_serverless() else settings.database_max_overflow,
    pool_pre_ping=True,
    pool_recycle=300,  # Recycle connections after 5 minutes
    # Disable prepared statements for pgbouncer compatibility (production only)
    connect_args={"statement_cache_size": 0} if settings.is_production_db else {},
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Create base class for models
Base = declarative_base()


# Dependency for FastAPI routes
async def get_db():
    """Get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Lifecycle management
async def init_db():
    """Initialize database (create tables if needed)"""
    async with engine.begin() as conn:
        # Import models to ensure they're registered
        from .models import database  # noqa
        # Create tables (in production, use Alembic migrations instead)
        # await conn.run_sync(Base.metadata.create_all)
        pass


async def close_db():
    """Close database connections"""
    await engine.dispose()
