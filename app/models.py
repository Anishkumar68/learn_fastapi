from unittest.mock import Base

class User(Base):
    __tablename__ = "user"

    id : Mapped[int] =mapped.int(primary) 
    Name:Mapped[str] = mapped.str(255)
    Email: Mapped[str] = mapped.str(255)