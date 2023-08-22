from config import API_KEY, DATABASE_PASSWORD, DATABASE_USERNAME, DATABASE, DATABASE_HOST, DATABASE_PORT, USER_ID
import requests
import time
import json
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table, URL
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import schedule
from db import url_object, User

def gather_data():
    # Основные данные
    base_url = 'https://api.vk.com/method/'

    groups_url = base_url + f'groups.get?user_id={USER_ID}&access_token={API_KEY}&v=5.131'

    groups_request = requests.get(groups_url)
    
    try:
        user_groups = groups_request.json().get("response").get("items")

    except AttributeError as exp:
        print("Запрос некорректен. Попробуйте проверить правильность и полноту введённых данных")

    posts = []
    posts_data = []
    c = 0
    for group in user_groups:
        wall_url = base_url + f'wall.get?owner_id=-{group}&count=6&access_token={API_KEY}&v=5.131'
        wall_request = requests.get(wall_url)
        for item in wall_request.json()["response"]["items"]:
            posts.append(item)
        time.sleep(0.4)
    for post in posts:

        # Разбираемся c простыми данными поста
        post_id = post["id"]
        post_text = post["text"]

        # Забираем дату и конвертируем её в обычный вид
        post_date  = post["date"]
        date = datetime.fromtimestamp(post_date)
        date = date.strftime('%Y-%m-%d %H:%M')

        # Смотрим, какие у поста есть закрепы
        attachments = post["attachments"]

        # Перебираем каждый закреп
        
        # Создаём словарь с данными
        data = {
            "post_id": post_id,
            "post_text": post_text,
            "post_date": date,
            "attachments": attachments
        }

        posts_data.append(data)
        try:
            engine = create_engine(url=url_object)
            session = Session(bind=engine)
            
        except IntegrityError:
            continue
    with open('data.json', 'w') as file: 
        json.dump(obj=posts_data, fp=file,indent=4, ensure_ascii=False)
def main():
    schedule.every(1).minutes.do(gather_data)
    gather_data()
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
     main()
