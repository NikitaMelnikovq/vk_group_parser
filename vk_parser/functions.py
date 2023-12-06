import requests
from config import API_KEY
from sqlalchemy.orm import Session
from db import Group
from datetime import datetime
import logging 
import sys
import time 

logging.basicConfig(filename=f'error_in_{sys.argv[0]}_{int(time.time())}.txt', level=logging.ERROR, format='%(asctime)s [%(levelname)s] - %(message)s')

def convert_time(timestamp: int) -> str:
    date = datetime.fromtimestamp(timestamp)
    return date.strftime('%Y-%m-%d %H:%M:%S')

def get_group_id(url: str) -> int:
    group_id = url.split("/")[-1]
    if group_id.startswith("club"):
        group_id = group_id.replace("club", "")
    else:
        group = requests.get(f"https://api.vk.com/method/groups.getById?group_id={group_id}&access_token={API_KEY}&v=5.154")
        if group.status_code == 200:
            group = group.json()
            try:
                group_id = group["response"]["groups"][0]["id"]
            except KeyError as error:
                logging.error(f"An error occurred: {error}", exc_info=True)
    return group_id

def get_group_name(group_id: int, session: Session) -> str:
    group_name = session.query(Group).filter(Group.group_id == group_id).first()
    return group_name.group_name if group_name else ""

def add_group_name(group_id: int) -> str:
    request_url = f"https://api.vk.com/method/groups.getById?group_id={abs(group_id)}&access_token={API_KEY}&v=5.154"
    response = requests.get(request_url)
    
    if response.status_code == 200:
        response = response.json()

    try:
        return response["response"]["groups"][0]["name"]
    except KeyError as error:
        logging.error(f"An error occurred: {error}", exc_info=True)
