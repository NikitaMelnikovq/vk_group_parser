from sqlalchemy import URL, Integer, Column, DateTime, JSON, Text, Boolean, INTEGER
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

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    join_time = Column(DateTime)
    updates = Column(Boolean)

class Post(Base):
    __tablename__ = "posts"
    group_name = Column(Text)
    post_id = Column(Integer, primary_key=True)
    post_text = Column(Text)
    post_date = Column(DateTime)
    video_urls = Column(JSON)
    image_urls = Column(JSON)
    audio_urls = Column(JSON)
    links = Column(JSON)
    doc_urls = Column(JSON)
    podcast_urls = Column(JSON)
    indentity_date = Column(Integer)

class UserGroups(Base):
    __tablename__ = "user_groups"
    group_id = Column(Integer, primary_key=True)
