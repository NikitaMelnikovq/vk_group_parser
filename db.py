from sqlalchemy import URL, Integer, Column, DateTime
from sqlalchemy.orm import declarative_base
from config import DATABASE_HOST, DATABASE_PASSWORD, DATABASE_PORT, DATABASE_USERNAME, DATABASE
from datetime import datetime
url_object = URL.create(
    "mysql+mysqlconnector",
    username=DATABASE_USERNAME,
    password=DATABASE_PASSWORD,
    host=DATABASE_HOST,
    port=DATABASE_PORT, 
    database=DATABASE
)   

Base = declarative_base()

class User(Base):
    __tablename__ = "Users"
    user_id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True)

class Post(Base):
    __tablename__ = "posts"
    post_id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now)
