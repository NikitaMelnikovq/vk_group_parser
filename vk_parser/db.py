from sqlalchemy import URL, Integer, Column, DateTime, Text, Boolean, VARCHAR
from sqlalchemy.orm import declarative_base
from config import DATABASE_HOST, DATABASE_PASSWORD, DATABASE_PORT, DATABASE_USERNAME, DATABASE

url_object = URL.create(
    "mysql+mysqlconnector",
    username=DATABASE_USERNAME,
    password=DATABASE_PASSWORD,
    host=DATABASE_HOST,
    port=DATABASE_PORT, 
    database=DATABASE
) 

url_object_async = URL.create(
    "mysql+aiomysql",
    username=DATABASE_USERNAME,
    password=DATABASE_PASSWORD,
    host=DATABASE_HOST,
    port=DATABASE_PORT, 
    database=DATABASE
)  
 
Base = declarative_base()

class Group(Base):
    __tablename__ = "vk_groups"
    group_id = Column(Integer, primary_key=True)
    group_name = Column(VARCHAR(250))

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    join_time = Column(DateTime, nullable=True)
    updates = Column(Boolean)
    want_updates = Column(Boolean)

class Post(Base):
    __tablename__ = "posts"
    group_name = Column(VARCHAR(length=250))
    post_id = Column(Integer, primary_key=True)
    post_text = Column(Text)
    post_link = Column(VARCHAR(length=250))
    post_date = Column(DateTime)
    identity_date = Column(Integer)
    sent = Column(Boolean, default=0)

class AllPosts(Base):
    __tablename__ = "all_posts"
    post_id = Column(Integer, primary_key=True)