from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./app.db"


engine = create_engine(
    DATABASE_URL, connect_args = {"check_same_thread" : False}
)

sessionLocal = sessionmaker(bind = engine, autoflush=False, autocommit = False)

def get_db():
    db = sessionLocal()

    try:
        yield db
    finally:
        db.close()