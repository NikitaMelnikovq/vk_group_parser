from db import UserGroups, url_object
from sqlalchemy import create_engine
from sqlalchemy.orm import Session



with open("groups.txt") as file:
    groups = file.readlines()
    groups = [int(group.strip()) for group in groups]
    engine = create_engine(url=url_object)
    session = Session(bind=engine)

    for group in groups:
        new_group = UserGroups(group_id=group)
        session.add(new_group)
    session.commit()
    session.close()