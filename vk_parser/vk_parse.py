import sys
import time
import requests
import schedule
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from config import API_KEY
from db import url_object, Post, Group, AllPosts
from functions import get_group_name, convert_time
import logging
logging.basicConfig(filename=f'error_in_{sys.argv[0]}{str(int(time.time()))}.txt', level=logging.ERROR, format='%(asctime)s [%(levelname)s] - %(message)s')

def gather_data_for_group(session: Session, group: Group) -> None:
    group_id = group.group_id
    group_name = get_group_name(group_id, session)

    try:
        posts = requests.get(f"https://api.vk.com/method/wall.get?owner_id=-{group_id}&count={3}&access_token={API_KEY}&v=5.199").json()["response"]["items"]

    except KeyError as error:
        logging.error(f"An error occurred: {error}", exc_info=True)

    time.sleep(0.2)
    
    for post in posts:
        post_id = post["id"]
        post_text = post["text"]
        post_date = post["date"]
        post_link = f"https://vk.com/wall{group_id}_{post_id}"

        date = convert_time(post_date)

        ids = [post.post_id for post in session.query(AllPosts).all()]

        if post_id in ids:
            continue
        
        unique_post = AllPosts(post_id=post_id)

        new_post = Post(
            group_name=group_name,
            identity_date=post_date,
            post_id=post_id,
            post_text=post_text,
            post_date=date,
            post_link=post_link
        )

        session.add(new_post)
        session.add(unique_post)

def gather_data():
    engine = create_engine(url=url_object)
    session = Session(bind=engine)

    groups = session.query(Group).all()

    for group in groups:
        gather_data_for_group(session, group)

    session.commit()
    session.close()

def main():
    schedule.every(10).minutes.do(gather_data)
    gather_data()

    while True:
        schedule.run_pending()
        time.sleep(3)

if __name__ == '__main__':
     main()
