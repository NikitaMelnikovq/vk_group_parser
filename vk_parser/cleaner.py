from sqlalchemy import create_engine, Delete
from sqlalchemy.orm import Session
from db import Post
import schedule
from db import url_object
import time

def clean_table():
    engine = create_engine(url=url_object)
    session = Session(bind=engine)
    
    stmt = Delete(Post).filter(Post.sent == 1).filter(int(time.time()) - Post.identity_date < 86400)
    session.execute(stmt)
    session.commit()
    session.close()

def main():
    schedule.every(15).seconds.do(clean_table)
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    main() 