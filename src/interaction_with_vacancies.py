import os
import psycopg2
from dotenv import load_dotenv


class DbManager():
    """Класс для подключения к БД PostgreSQL"""

    def __init__(self):
        """Инициализация класса DBManager."""
        load_dotenv()
        self.host = os.getenv("DATABASE_HOST") or "localhost"
        self.port = os.getenv("DATABASE_PORT") or "5432"
        self.user = os.getenv("DATABASE_USER") or "postgres"
        self.password = os.getenv("DATABASE_PASSWORD")
        self.database = os.getenv("DATABASE_NAME") or "vacancies"
        self.conn = None



    def get_companies_and_vacancies_count():
        """Метод получает список всех компаний и количество вакансий у каждой компании"""



    def get_all_vacancies():
        """Метод получает список всех вакансий с указанием названия компании, названия вакансии и зарплаты
                               и ссылки на вакансию"""



    def get_avg_salary():
        """Метод получает среднюю зарплату по вакансиям"""



    def get_vacancies_with_higher_salary():
        """Метод получает список всех вакансий, у которых зарплата выше средней по всем вакансиям."""



    def get_vacancies_with_keyword():
        """Метод получает список всех вакансий, в названии которых содержатся переданные в метод слова"""