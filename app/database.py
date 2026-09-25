from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession,create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings
# the sqlite path where the file will be created and a connection will be stablized with it 
# DATABASE_URL = os.getenv("DATABASE_URL")
# engine is connection manager with database
# we are using the sqlite thats why we passed the connect_args 
engine = create_async_engine(settings.DATABASE_URL, connect_args= {"check_same_thread" : False})


# to store session with database
sessionLocal = sessionmaker(bind=engine, autocommit =False, autoflush=False)

class Base(declarative_base):
    pass


# dependancy 
def get_db():
    with sessionLocal() as db:
        yield db

    # db = sessionLocal()

    # try:
    #     yield db
    # finally:
    #     db.close()