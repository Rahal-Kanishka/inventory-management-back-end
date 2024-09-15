from decouple import config

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# DB_URL = 'mysql+pymysql://root:root1234@host.docker.internal:3306/intelicheff'
DB_URL = config('DB_URL')
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
