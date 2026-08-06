import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db_url = os.getenv("DATABASE_URL", "postgresql://postgres:vinayakrm073%40@localhost:5432/postgres")
engine = create_engine(db_url)
session = sessionmaker(autoflush=False, autocommit = False, bind=engine)