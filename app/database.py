import os
import sqlalchemy
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine


db_user = os.environ["DB_USER"]
db_pass = os.environ["DB_PASSWORD"]
db_host = os.environ["DB_HOST"]
db_name = os.environ["DB_NAME"]
url = f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}/{db_name}"
engine = create_engine(url)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


def init_db():
    import models

    Base.metadata.create_all(bind=engine)
