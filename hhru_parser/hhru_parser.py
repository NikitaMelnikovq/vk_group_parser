import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from db import url_object, Vacancy

def get_companies() -> None:
    engine = create_engine(url=url_object)
    session = Session(bind=engine, expire_on_commit=False)

    company_ids = session.query()

    for company_id in company_ids:
        url = f'https://api.hh.ru/vacancies?employer_id={company_id}'
        get_vacancies(url=url, session=session)

    session.commit()
    session.close()
    
def get_vacancies(url, session: Session) -> None:
    vacancies = requests.get(url).json()["items"]

    for vacancy in vacancies:
        if not vacancy["type"]["name"] == "Открытая":
            continue

        vacancy_id = vacancy["id"]
        vacancy_name = vacancy["name"]
        vacancy_town = vacancy["area"]["name"]
        salary_from = vacancy["salary"]["from"]
        salary_to = vacancy["salary"]["to"]
        salary = "от" + str(salary_from) + "до" + str(salary_to) if salary_to is not None else "от" + str(salary_from)
        vacancy_url = vacancy["alternate_url"]
        alternate_url_resp = vacancy["apply_alternate_url"]
        vacancy_description = vacancy["description"]
        vacancy_employment = vacancy["employment"]["name"]
        vacancy_experience = vacancy["experience"]["name"]
        vacancy_schedule = vacancy["schedule"]["name"]

        new_vacancy = Vacancy(vacancy_id=vacancy_id,
                              vacancy_name=vacancy_name,
                              vacancy_town=vacancy_town,
                              vacancy_salary=salary,
                              vacancy_url=vacancy_url,
                              alternate_url_resp=alternate_url_resp,
                              vacancy_employment=vacancy_employment,
                              vacancy_description=vacancy_description,
                              vacancy_experience=vacancy_experience,
                              vacancy_schedule=vacancy_schedule)
        session.add(new_vacancy)
        

def main() -> None:
    get_companies() 

if __name__ == "__main__":
    main()