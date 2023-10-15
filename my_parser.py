from config import API_KEY, API_VIDEO_KEY
import requests
import time
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import schedule
from db import url_object, Post, UserGroups

def gather_data():
    # Основные данные
    base_url = 'https://api.vk.com/method/'
    f_engine = create_engine(url=url_object)
    f_session = Session(bind=f_engine)

    # Получаем необходимые для парсинга группы
    user_groups = [group.group_id for group in f_session.query(UserGroups).all()]
    f_session.commit()
    f_session.close()
    posts = []

    # Обрабатываем необходимые для парсинга группы
    for group in user_groups:
        wall_url = base_url + f'wall.get?owner_id=-{group}&count=6&access_token={API_KEY}&v=5.131'
        wall_request = requests.get(wall_url)
        for item in wall_request.json()["response"]["items"]:
            posts.append(item)
        time.sleep(0.2)
    
    # Обрабатываем каждый пост
    for post in posts:
        # Разбираемся c простыми данными поста
        post_id = post["id"]
        post_text = post["text"]
        
        # Забираем название группы
        group = post["owner_id"]
        group_url = base_url + f"groups.getById?group_id={abs(group)}&access_token={API_KEY}&v=5.131"
        group_name = requests.get(group_url).json()["response"][0]["name"]
        post_link = f"https://vk.com/wall{group}_{post_id}"
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
                    urls["Audio"].append(audio["url"])

        # Записываем данные в БД
        engine = create_engine(url=url_object)
        session = Session(bind=engine)
        ids = [post.post_id for post in session.query(Post).all()]
        if post_id in ids:
            continue 
        else:
            new_post = Post()
            new_post.post_id = post_id
            new_post.identity_date = post_date
            new_post.post_date = date
            new_post.group_name = group_name
            new_post.post_text = post_text
            new_post.post_link = post_link
            new_post.links = urls["Link"]
            new_post.doc_urls = urls["Document"]
            new_post.image_urls = urls["Photo"]
            new_post.audio_urls = urls["Audio"]
            new_post.video_urls = urls["Video"]
            new_post.podcast_urls = urls["Podcasts"]
            session.add(new_post)        
        session.commit()
        session.close()

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
