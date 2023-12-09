import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from vk_parser.db import url_object

def get_companies():
    engine = create_engine(engine=url_object)
    session = Session(bind=engine)
    
    company_ids = session.query()

    for company_id in company_ids:
        url = f'https://api.hh.ru/vacancies?employer_id={company_id}'

    
def get_vacancies(url):
    vacancies = requests.get(url).json()["items"]

    for vacancy in vacancies:
        vacancy_id = vacancy["id"]
        vacancy_name = vacancy["name"]
        vacancy_town = vacancy["area"]["name"]
        salary_from = vacancy["salary"]["from"]
        salary_to = vacancy["salary"]["to"]
        salary = "от" + str(salary_from) + "до" + str(salary_to) if salary_to is not None else "от" + str(salary_from)
        
def main():
    get_companies() 

if __name__ == "__main__":
    main()