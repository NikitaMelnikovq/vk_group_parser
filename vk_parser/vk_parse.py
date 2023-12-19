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

def make_request(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return response.json()["response"]["items"]
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}", exc_info=True)
        return None
    except KeyError as e:
        logging.error(f"KeyError: {e}", exc_info=True)
        return None

def gather_data_for_group(session: Session, group: Group) -> None:
    group_id = group.group_id
    group_name = get_group_name(group_id, session)

    url = f"https://api.vk.com/method/wall.get?owner_id=-{group_id}&count={3}&access_token={API_KEY}&v=5.199"
    max_retries = 3

    for retry in range(max_retries):
        posts = make_request(url)

        if posts is not None:
            break

        time.sleep(3600)  # Adjust the delay as needed

    else:
        logging.error(f"Max retries reached. Unable to obtain data for group {group_id}")
        return

    time.sleep(0.2)
    
    for post in posts:
        post_id = post["id"]
        post_text = post["text"]
        post_date = post["date"]
        post_link = f"https://vk.com/wall-{group_id}_{post_id}"

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
    with Session(bind=engine) as session:
        groups = session.query(Group).all()

        for group in groups:
            gather_data_for_group(session, group)

        session.commit()
        session.close()

def main():
    schedule.every(10).minutes.do(gather_data)

    while True:
        schedule.run_pending()
        time.sleep(3)

if __name__ == '__main__':
    main()
