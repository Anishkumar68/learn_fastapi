from sqlalchemy import DeclarativeBase, Mapped, mapped

class Base(DeclarativeBase):
    pass
class User(Base):
    __tablename__ = "user"

    id : Mapped[int] =mapped.int(primary = True) 
    Name:Mapped[str] = mapped.str(100)
    Email: Mapped[str] = mapped.str(255)

class Post(Base):
    __tablename__ = "post"

    id:Mapped[int] = mapped.int(primary = True)
    title:Mapped[str] = mapped.str(200)
    description:Mapped[str] = mapped.str(500)
    likes:Mapped[int] = mapped.int()
    comments:Mapped[int] = mapped.int()
    longtext:Mapped[str] = mapped.str(1000)

class Comment(Base):
    __tablename__ = "comment"

    id:Mapped[int] = mapped.int(primary = True)
    comment:Mapped[str] = mapped.str(500)
    post_id:Mapped[int] = mapped.int()


