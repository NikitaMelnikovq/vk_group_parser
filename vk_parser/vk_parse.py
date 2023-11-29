from config import API_KEY
import requests
import time
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import schedule
from db import url_object, Post, Group
from functions import get_group_name, create_error_log, convert_time

def gather_data():
    engine = create_engine(url=url_object) 
    session = Session(bind=engine)

    groups = session.query(Group).all()

    for group in groups:
        group_id = group.group_id
        group_name = get_group_name(group_id)

        posts = []

        try:
            posts = requests.get(f"https://api.vk.com/method/wall.get?owner_id={group_id}&count={3}&access_key={API_KEY}&v=5.154").json()["response"]["items"]
        except KeyError as error:
            create_error_log(str(error))

        time.sleep(0.2)

        for post in posts:
            post_id = post["id"]
            post_text = post["text"]
            post_date  = post["date"]
            post_link = f"https://vk.com/wall{group_id}_{post_id}"

            date = convert_time(post_date)

            ids = [post.post_id for post in session.query(Post).all()]

            if post_id in ids:
                continue 

            new_post = Post()
            new_post.group_name = group_name
            new_post.identity_date = post_date
            new_post.post_id = post_id
            new_post.post_text = post_text
            new_post.post_date = date 
            new_post.post_link = post_link
            session.add(new_post)
    session.commit()
    session.close()

def main():
    schedule.every(15).minutes.do(gather_data)
    gather_data()

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
     main()
