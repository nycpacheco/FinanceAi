from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Por enquanto vamos usar SQLite para facilitar, depois podemos mudar para PostgreSQL
SQLALCHEMY_DATABASE_URL = "sqlite:///./financeai.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()