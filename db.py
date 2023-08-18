from sqlalchemy import create_engine, MetaData, Table, URL
from sqlalchemy.orm import Session
from config import DATABASE_HOST, DATABASE_PASSWORD, DATABASE_PORT, DATABASE_USERNAME, DATABASE
url_object = URL.create(
    "mysql+mysqlconnector",
    username=DATABASE_USERNAME,
    password=DATABASE_PASSWORD,
    host=DATABASE_HOST,
    port=DATABASE_PORT,
    database=DATABASE
)   

engine = create_engine(url_object)

metadata = MetaData()
my_table = Table('posts', metadata, autoload_with=engine)

session = Session(bind=engine)

new_record = my_table.insert().values(post_id="87")

session.execute(new_record)

session.commit()

session.close()