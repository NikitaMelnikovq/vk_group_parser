from sqlalchemy import create_engine, Delete
from sqlalchemy.orm import Session
from db import Post
import schedule
from db import url_object
import time, requests 
from config import API_KEY
from datetime import timedelta
def clean_table():
    engine = create_engine(url=url_object)
    session = Session(bind=engine)
    stmt = Delete(Post).filter(int(time.time()) - Post.identity_date >= 86400)
    session.execute(stmt)
    session.commit()
    session.close()

def main():
    schedule.every(1).days.do(clean_table)
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main() 