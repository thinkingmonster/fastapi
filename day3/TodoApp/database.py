from sqlalchemy import create_engine, engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 1. Define where database is
SQLALCHEMY_DATABASE_URL = "sqlite:///./todos.db"
# 2. Create engine (connection manager)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
# 3. Create session factory (for making "conversations" with DB)
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)
# 4. Create base class (for defining tables)
Base = declarative_base()
