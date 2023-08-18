from config import API_KEY, DATABASE_PASSWORD, DATABASE_USERNAME, DATABASE, DATABASE_HOST, DATABASE_PORT, USER_ID
import requests
import time
import json
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table, URL
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import schedule

def database_interaction(post_id):
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

    new_record = my_table.insert().values(post_id=post_id)

    session.execute(new_record)

    session.commit()

    session.close()

def gather_data():
    # Основные данные
    base_url = 'https://api.vk.com/method/'


    # Айди юзера, для которого надо собрать посты

    groups_url = base_url + f'groups.get?user_id={USER_ID}&access_token={API_KEY}&v=5.131'

    groups_request = requests.get(groups_url)
    
    try:
        user_groups = groups_request.json().get("response").get("items")

    except AttributeError as exp:
        print("Запрос некорректен. Попробуйте проверить правильность и полноту введённых данных")

    posts = []
    posts_data = []

    for group in user_groups:

        wall_url = base_url + f'wall.get?owner_id=-{group}&count=6&access_token={API_KEY}&v=5.131'
        wall_request = requests.get(wall_url)
        posts.append(wall_request.json()["response"]["items"])
        time.sleep(0.4)
    for post in posts:

        # Разбираемся c простыми данными поста
        post_id = post[0]["id"]
        post_text = post[0]["text"]

        # Забираем дату и конвертируем её в обычный вид
        post_date  = post[0]["date"]
        date = datetime.fromtimestamp(post_date)
        date = date.strftime('%Y-%m-%d %H:%M')

        # Создаём массив для сохранения url изображений
        img_urls = []

        # Смотрим, какие у поста есть закрепы
        attachments = post[0]["attachments"]

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
            database_interaction(post_id=post_id)
        except IntegrityError:
            continue
    with open('data.json', 'w') as file: 
        json.dump(obj=posts_data, fp=file,indent=4, ensure_ascii=False)
def main():
    schedule.every(15).minutes.do(gather_data)
    gather_data()
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
     main()
