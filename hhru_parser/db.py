from vk_parser.config import DATABASE_HOST, DATABASE_PASSWORD, DATABASE_PORT, DATABASE_USERNAME, DATABASE
from sqlalchemy import URL, INTEGER, Column, VARCHAR, TEXT, BOOLEAN
from sqlalchemy.ext.declarative import declarative_base

url_object = URL.create(
    "mysql+mysqlconnector",
    username=DATABASE_USERNAME,
    password=DATABASE_PASSWORD,
    host=DATABASE_HOST,
    port=DATABASE_PORT, 
    database="job_parser_data"
) 

Base = declarative_base()

class Vacancy(Base):
    __tablename__ = "vacancies"
    vacancy_id = Column(INTEGER, primary_key=True)
    vacancy_name = Column(VARCHAR(250))
    vacancy_town = Column(VARCHAR(250))
    vacancy_salary = Column(VARCHAR(250))
    vacancy_url = Column(VARCHAR(250))
    vacancy_description = Column(TEXT)
    alternate_url_resp = Column(VARCHAR(300))
    vacancy_employment = Column(VARCHAR(100))
    vacancy_experience = Column(VARCHAR(50))
    vacancy_schedule = Column(VARCHAR(50))
    sent = Column(BOOLEAN, default=0)
    created_at = Column(INTEGER)

class User(Base):
    __tablename__ = "users"
    user_id = Column(INTEGER, primary_key=True)
    hh_updates = Column(BOOLEAN)
    kwork_updates = Column(BOOLEAN)
    fl_updates = Column(BOOLEAN)
    habr_updates = Column(BOOLEAN)