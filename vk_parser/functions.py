import requests
from config import API_KEY
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from db import url_object, Group
import os, time 
from datetime import datetime

def convert_time(tmsp: int) -> str:
    date = datetime.fromtimestamp(tmsp)
    date = date.strftime('%Y-%m-%d %H:%M:%S')
    return date

def create_error_log(error: Exception) -> None:
    if not os.path.exists("error_logs"):
        os.mkdir("error_logs")
        os.chdir("error_logs")
    with open(f"{time.time()}.txt", 'w') as file:
        file.write(error.with_traceback())

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
                log = str(group) + "\n" + str(error)
                create_error_log(log)
    return group_id
    
def get_group_name(group_id: int) -> str:
    engine = create_engine(url=url_object)
    session = Session(bind=engine)
    group_name = session.query(Group).filter(Group.group_id==group_id).first()
    if group_name is None:
        return group_name
    else:
        return group_name.group_name

def add_group_name(group_id: int) -> str:
    request_url = f"https://api.vk.com/method/groups.getById?group_id={abs(group_id)}&access_token={API_KEY}&v=5.154"
    response = requests.get(request_url)
    if response.status_code == 200:
        response = response.json()
    try:
        response = response["response"]["groups"][0]["name"]
        return str(response)
    except KeyError as error:
        log = str(response) + "\n" + str(error)
        create_error_log(log)