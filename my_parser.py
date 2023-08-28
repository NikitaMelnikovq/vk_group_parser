from config import API_KEY, DATABASE_PASSWORD, DATABASE_USERNAME, DATABASE, DATABASE_HOST, DATABASE_PORT, USER_ID, API_VIDEO_KEY
import requests
import time
import json
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table, URL
from sqlalchemy.orm import Session
import os
from sqlalchemy.exc import IntegrityError
import schedule
from db import url_object, User, Post

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
        time.sleep(0.2)
    with open("data.json", 'w') as file:
        json.dump(obj=posts, fp=file, indent=4, ensure_ascii=False)
    for post in posts:
        
        # Разбираемся c простыми данными поста
        post_id = post["id"]
        post_text = post["text"]

        # Забираем название группы
        group = post["owner_id"]
        group_url = base_url + f"groups.getById?group_id={abs(group)}&access_token={API_KEY}&v=5.131"
        group_name = requests.get(group_url).json()["response"][0]["name"]
        time.sleep(0.2)
        # Забираем дату и конвертируем её в обычный вид
        post_date  = post["date"]
        date = datetime.fromtimestamp(post_date)
        date = date.strftime('%Y-%m-%d %H-%M-%S')

        # Смотрим, какие у поста есть закрепы
        attachments = post["attachments"]

        # Работаем с закрепами 
        urls = {
            "Video": [],
            "Audio": [],
            "Photo": [],
            "Link": [],
            "Document": [],
            "Podcasts": []
        }
        if len(attachments) > 0:
            for attachment in attachments:
                # Обрабатываем фото
                if attachment["type"] == "photo":
                    photo = attachment.get("photo")
                    sizes = photo.get("sizes")
                    for size in sizes:
                        if size["type"] == 'x':
                            urls["Photo"].append(size["url"])

                # Обрабатываем документы
                if attachment["type"] == "doc":
                    doc = attachment.get("doc")
                    urls["Document"].append(doc["url"])

                # Обрабатываем ссылки
                if attachment["type"] == 'link':
                    link = attachment.get("link")
                    urls["Link"].append(link["url"])

                # Обрабатываем аудио
                if attachment["type"] == 'audio':
                    audio = attachment.get("audio")
                    urls["Audio"].append(audio["audio"])
                # Обрабатываем видео
                if attachment["type"] == 'video':
                    video = attachment["video"]
                    owner_id = video.get("owner_id")
                    video_id = video.get("id")
                    video_url = base_url+ f"video.get?video={owner_id}_{video_id}&access_token={API_VIDEO_KEY}&v=5.131"
                    video_request = requests.get(video_url).json()
                    videos = video_request.get("response").get("items")
                    for vid in videos:
                        urls["Video"].append(vid.get("player"))
                if attachment["type"] == 'podcast':
                    podcast = attachment.get("podcast")
                    urls["Podcasts"].append(podcast["url"])

        # работаем с БД
        engine = create_engine(url=url_object)
        session = Session(bind=engine)
        ids = [post.post_id for post in session.query(Post).all()]

        if post_id in ids:
            continue 
        else:
            new_post = Post()
            new_post.post_id = post_id
            new_post.links = urls["Link"]
            new_post.doc_urls = urls["Document"]
            new_post.image_urls = urls["Photo"]
            new_post.audio_urls = urls["Audio"]
            new_post.video_urls = urls["Video"]
            new_post.podcast_urls = urls["Podcasts"]
            new_post.post_date = date
            new_post.group_name = group_name
            new_post.post_text = post_text
            session.add(new_post)        
            session.commit()
            session.close()

    #     # Создаём словарь с данными
    #     data = {
    #         "group_name": group_name,
    #         "post_id": post_id,
    #         "post_text": post_text,
    #         "post_date": date,
    #         "attachments": attachments,
    #     }

    #     # Добавление поста в массив для дальнейшей записи в файл
    #     posts_data.append(data)

    # # создаём папку и файл, если таковых нет
    # if not os.path.exists('data.json'):

    #     # Создаём файл
    #     with open('data.json', 'w') as f:
    #         print(f"File {f.name} was created succesfully!")
    
    # # сохраняем полученные данные в файл
    # if len(posts_data) > 0:
    #     with open('data.json', 'r+') as file: 
    #         for post_data in posts_data:
    #             json.dump(obj=post_data,fp=file, ensure_ascii=False, indent=4)
def main():
    # запускаем таймер на каждую минуту
    schedule.every(1).minutes.do(gather_data)
    gather_data()

    # запускаем парсер
    while True:
        schedule.run_pending()
        time.sleep(1)

# Входная точка программы
if __name__ == '__main__':
     main()
