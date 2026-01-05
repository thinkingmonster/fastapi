from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# 1. Define where database is
# PostgreSQL connection string format: postgresql://username:password@host:port/database
# For local development, using environment variable with fallback to default
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://akashthakur@localhost:5432/todosapp"
)

# 2. Create engine (connection manager)
# PostgreSQL doesn't need check_same_thread (that's SQLite-specific)
engine = create_engine(DATABASE_URL)

# 3. Create session factory (for making "conversations" with DB)
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

# 4. Create base class (for defining tables)
Base = declarative_base()
