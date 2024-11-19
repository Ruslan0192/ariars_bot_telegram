from sqlalchemy import DateTime, String, Text, func, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class General(Base):
    __tablename__ = 'General'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_name: Mapped[str] = mapped_column(String(50),  nullable=True)
    name: Mapped[str] = mapped_column(String(50), nullable=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    value: Mapped[float] = mapped_column(nullable=True)
    picture: Mapped[str] = mapped_column(String(150), nullable=True)


class Category_question(Base):
    __tablename__ = 'Category_question'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    picture: Mapped[str] = mapped_column(String(150), nullable=True)
    # categories: Mapped[list['Questions']] = relationship("Questions", back_populates="category_question")



class Questions(Base):
    __tablename__ = 'Questions'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger)
    # category_question_id: Mapped[int] = mapped_column(ForeignKey(column='Category_question.id'))
    category_question_id: Mapped[int] = mapped_column()
    parents_id: Mapped[int] = mapped_column(default=0)
    question_text: Mapped[str] = mapped_column(String(255), nullable=True)
    answer_text: Mapped[str] = mapped_column(String(255), nullable=True)
    frozen: Mapped[bool] = mapped_column(default=False)
    # category_question: Mapped['Category_question'] = relationship('Category_question', back_populates='categories')


class Question_pictures(Base):
    __tablename__ = 'Question_pictures'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(nullable=True)
    picture: Mapped[str] = mapped_column(String(150), nullable=True)
    caption: Mapped[str] = mapped_column(Text, nullable=True)


class User(Base):
    __tablename__ = 'User'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    name: Mapped[str] = mapped_column(String(50), nullable=True)
    telefon: Mapped[str] = mapped_column(String(20), nullable=True)


class Admin(Base):
    __tablename__ = 'Admin'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    user: Mapped[bool] = mapped_column(default=False)
    superadmin: Mapped[bool] = mapped_column(default=False)


class Product_cat(Base):
    __tablename__ = 'Product_cat'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)


class Product_cat_type(Base):
    __tablename__ = 'Product_cat_type'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cat_name: Mapped[str] = mapped_column(String(50), nullable=False)
    type_name: Mapped[str] = mapped_column(String(50), nullable=True)
    picture: Mapped[str] = mapped_column(String(150), nullable=True)


class Products(Base):
    __tablename__ = 'Products'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    parents_id: Mapped[int] = mapped_column()
    name: Mapped[str] = mapped_column(String(50))
    cat_id: Mapped[int] = mapped_column()
    price: Mapped[float] = mapped_column()
    color: Mapped[str] = mapped_column(String(25))
    size: Mapped[str] = mapped_column(String(10))
    gender: Mapped[str] = mapped_column(String(10))
    composition: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(Text)
    link: Mapped[str] = mapped_column(String(255))
    frozen: Mapped[bool] = mapped_column(default=False)


class Product_pictures(Base):
    __tablename__ = 'Product_pictures'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(nullable=True)
    picture: Mapped[str] = mapped_column(String(150), nullable=True)
    frozen: Mapped[bool] = mapped_column(default=False)


class Product_composition(Base):
    __tablename__ = 'Product_composition'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=True)


class Product_color(Base):
    __tablename__ = 'Product_color'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=True)


class Product_size(Base):
    __tablename__ = 'Product_size'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=True)


class Product_gender(Base):
    __tablename__ = 'Product_gender'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=True)

class Question_for_devoloper(Base):
    __tablename__ = 'Question_for_devoloper'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(String(255), nullable=True)




