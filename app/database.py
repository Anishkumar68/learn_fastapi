from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# the sqlite path where the file will be created and a connection will be stablized with it 
DATABASE_URL = "sqlite:///./app.db"

# engine is connection manager with database
# we are using the sqlite thats why we passed the connect_args 
engine = create_engine(DATABASE_URL, connect_args= {"check_same_thread" : False})


# to store session with database
sessionLocal = sessionmaker(bind=engine, autocommit =False, autoflush=False)

# dependancy 
def get_db():
    db = sessionLocal()

    try:
        yield db
    finally:
        db.close()