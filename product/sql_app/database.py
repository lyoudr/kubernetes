from sqlalchemy import create_engine 
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.orm import sessionmaker

import os
# Read PostgreSQL environment variables
postgres_host = os.environ.get("POSTGRES_HOST", "localhost")
postgres_port = os.environ.get("POSTGRES_PORT", "5432")
postgres_db = os.environ.get("POSTGRES_DB", "ann")
postgres_user = os.environ.get("POSTGRES_USER", "ann")
postgres_password = os.environ.get("POSTGRES_PASSWORD", "")

SQLALCHEMY_DATABASE_URL = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://ann:annpasswd@127.0.0.1:3306/practice"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()