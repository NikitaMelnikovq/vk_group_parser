from sqlalchemy import create_engine, MetaData, Table, URL, Integer, Column
from sqlalchemy.orm import Session
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

Base = declarative_base()

class User(Base):
    __tablename__ = "Users"
    user_id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True)