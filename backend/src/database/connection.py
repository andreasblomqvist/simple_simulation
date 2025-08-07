"""
Database connection setup for SimpleSim PostgreSQL database
"""
import os
from typing import Optional, AsyncGenerator
import logging
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.engine import URL
from sqlalchemy.pool import QueuePool

# Setup logging
logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration from environment variables"""
    
    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = int(os.getenv("DB_PORT", "5432"))
        self.database = os.getenv("DB_NAME", "simplesim")
        self.username = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "password")
        self.schema = os.getenv("DB_SCHEMA", "public")
        
        # Connection pooling settings
        self.pool_size = int(os.getenv("DB_POOL_SIZE", "10"))
        self.max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "20"))
        self.pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", "30"))
        self.pool_recycle = int(os.getenv("DB_POOL_RECYCLE", "1800"))  # 30 minutes
        
        # SSL settings for production
        self.ssl_mode = os.getenv("DB_SSL_MODE", "prefer")
        
    @property
    def database_url(self) -> str:
        """Get the database URL for async connections"""
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
            query={"sslmode": self.ssl_mode}
        )


class DatabaseManager:
    """Database connection manager with connection pooling and session handling"""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        self.config = config or DatabaseConfig()
        self._engine = None
        self._session_factory = None
        
    def _create_engine(self):
        """Create async database engine with connection pooling"""
        if self._engine is None:
            self._engine = create_async_engine(
                self.config.database_url,
                poolclass=QueuePool,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_timeout=self.config.pool_timeout,
                pool_recycle=self.config.pool_recycle,
                pool_pre_ping=True,  # Validate connections before use
                echo=os.getenv("DB_ECHO", "false").lower() == "true",  # Log SQL queries in development
                future=True,
            )
            logger.info(f"Created database engine for {self.config.host}:{self.config.port}/{self.config.database}")
        
        return self._engine
    
    def _create_session_factory(self):
        """Create session factory for database sessions"""
        if self._session_factory is None:
            engine = self._create_engine()
            self._session_factory = async_sessionmaker(
                engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=True,
                autocommit=False
            )
            
        return self._session_factory
    
    async def get_session(self) -> AsyncSession:
        """Get a new database session"""
        session_factory = self._create_session_factory()
        return session_factory()
    
    @asynccontextmanager
    async def get_session_context(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session with automatic cleanup"""
        session = await self.get_session()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    async def execute_transaction(self, func, *args, **kwargs):
        """Execute a function within a database transaction"""
        async with self.get_session_context() as session:
            return await func(session, *args, **kwargs)
    
    async def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            async with self.get_session_context() as session:
                result = await session.execute("SELECT 1")
                return result.scalar() == 1
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    async def close(self):
        """Close database connections"""
        if self._engine:
            await self._engine.dispose()
            logger.info("Database engine disposed")


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_database_manager() -> DatabaseManager:
    """Get the global database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


async def get_db_session() -> AsyncSession:
    """FastAPI dependency for getting database session"""
    db_manager = get_database_manager()
    return await db_manager.get_session()


# FastAPI dependency for database sessions
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides database session with automatic cleanup"""
    db_manager = get_database_manager()
    async with db_manager.get_session_context() as session:
        yield session


async def init_database():
    """Initialize database connection for FastAPI startup"""
    db_manager = get_database_manager()
    
    # Test database connection
    is_healthy = await db_manager.health_check()
    if is_healthy:
        logger.info("Database connection established successfully")
    else:
        logger.error("Failed to establish database connection")
        raise RuntimeError("Database connection failed")
    
    return db_manager


async def close_database():
    """Close database connections for FastAPI shutdown"""
    global _db_manager
    if _db_manager:
        await _db_manager.close()
        _db_manager = None