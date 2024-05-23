from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


host = 'aws-0-ap-southeast-1.pooler.supabase.com'
db_name = 'postgres'
port = 5432
user = 'postgres.hyhxbqsvpvtbarfxwrow'
password = 'sehatinnonauthentication'

SQLALCHEMY_DATABASE_URL = 'postgresql://' + user + ':' + password + '@' + host + ':' + str(port) + '/' + db_name

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
