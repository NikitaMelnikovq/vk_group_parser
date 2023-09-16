from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from db import url_object
with open('groups.txt') as file:

    engine = create_engine(url=url_object)

    session = Session(bind=engine)

    groups = list(filter(lambda x: int(x.strip()), file.readlines()))
    
    for group in groups: 
        session.execute(statement=text(f"INSERT INTO user_groups VALUES ({group});"))
    session.commit()
    session.close() 