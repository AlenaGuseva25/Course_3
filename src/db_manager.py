import os
from typing import Any

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def create_database():

    conn = psycopg2.connect(
        host=os.getenv("DATABASE_HOST"),
        port=os.getenv("DATABASE_PORT"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD"),
    )

    conn.autocommit = True
    print("Соединение с PostgreSQL установлено.")

    cur = conn.cursor()
    load_dotenv()

    name = os.getenv("DATABASE_NAME")
    cur.execute(f" DROP DATABASE IF EXISTS {name}")
    cur.execute(f"CREATE DATABASE {name}")
    print("База данных создана успешно.")

    conn.commit()
    conn.close()
    print("Соединение с БД закрыто.")

    return "Database operation completed."


def create_tables():
    conn = psycopg2.connect(
        host=os.getenv("DATABASE_HOST"),
        port=os.getenv("DATABASE_PORT"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD"),
        database=os.getenv("DATABASE_NAME"),
    )
    cur = conn.cursor()
    with conn.cursor() as cur:
        cur.execute(
            """
        DROP TABLE IF EXISTS organizations CASCADE;
        CREATE TABLE organizations (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        url TEXT NOT NULL,
        open_vacancy INTEGER NOT NULL)
        """
        )
        conn.commit()
    conn.close()

    conn = psycopg2.connect(
        host=os.getenv("DATABASE_HOST"),
        port=os.getenv("DATABASE_PORT"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD"),
        database=os.getenv("DATABASE_NAME"),
    )

    with conn.cursor() as cur:
        cur.execute(
            """
            DROP TABLE IF EXISTS vacancies CASCADE;
            CREATE TABLE vacancies (
            vacancy_id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            salary_from INT,
            salary_to INT,
            vacancies_url TEXT NOT NULL,
            employer_id INT REFERENCES organizations(id)
            )
            """
        )
        conn.commit()
    conn.close()
    return "База данных создана"


def save_data_to_db(data_organizations: list[dict], data_vacancies: list[dict]):

    try:
        conn = psycopg2.connect(
            host=os.getenv("DATABASE_HOST"),
            port=os.getenv("DATABASE_PORT"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
            database=os.getenv("DATABASE_NAME"),
        )

        with conn.cursor() as cur:
            for org in data_organizations:
                id = org["id"]
                name = org["name"]
                url = org["url"]
                open_vacancies = org["open vacancies"]
                cur.execute(
                    """
                    INSERT INTO organizations (id, name, url, open_vacancy)
                    VALUES (%s, %s, %s, %s)
                """,
                    (id, name, url, open_vacancies),
                )

            for vacancy in data_vacancies:
                vacancy_id = vacancy.get("vacancy_id")
                name = vacancy["name"]
                url = vacancy["url"]
                salary_from = vacancy["salary"].get("from", 0)
                salary_to = vacancy["salary"].get("to", 0)
                employer_id = vacancy["employer_id"]

                cur.execute(
                    """
                    INSERT INTO vacancies (vacancy_id, name, salary_from, salary_to, vacancies_url, employer_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """,
                    (vacancy_id, name, salary_from, salary_to, url, employer_id),
                )

            conn.commit()
            print("Данные успешно сохранены в базу данных.")

    except psycopg2.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")

    finally:
        conn.commit()
        conn.close()
        print("Соединение с БД закрыто.")

    return "База данных полностью заполнена."


class DBManager:

    def __init__(self):
        load_dotenv()
        self.conn = psycopg2.connect(
            host=os.getenv("DATABASE_HOST"),
            port=os.getenv("DATABASE_PORT"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
            database=os.getenv("DATABASE_NAME"),
        )

    def get_companies_and_vacancies_count(self) -> list[tuple]:
        """
        Получает список всех компаний и количество вакансий у каждой компании
        """
        conn = self.conn
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT name, open_vacancy FROM organizations
                """
            )
            result = cur.fetchall()
            conn.commit()
        conn.close()
        return result

    def get_all_vacancies(self) -> Any:
        """
        Получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию
        """
        conn = self.conn
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT * FROM vacancies
                """
            )
            total = cur.fetchall()
            conn.commit()
        conn.close()
        return total

    def get_avg_salary(self) -> float:
        """
        Получает среднюю зарплату по вакансиям
        """
        conn = self.conn
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT ((SUM(salary_to) + SUM(salary_from)) / 2) / COUNT(*) AS avg_salary FROM vacancies
                """
            )
            avg_salary = cur.fetchone()[0]
            conn.commit()
        return avg_salary

    def get_vacancies_with_higher_salary(self) -> list[tuple]:
        """
        Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям
        """
        conn = self.conn
        avg_salary = self.get_avg_salary()
        conn = self.conn
        with conn.cursor() as cur:
            cur.execute(
                """
               SELECT * FROM vacancies WHERE (salary_to + salary_from) / 2 > %s
                """,
                [avg_salary],
            )
            vacancies = cur.fetchall()
            conn.commit()
        conn.close()
        return vacancies

    def get_vacancies_with_keyword(self, word: str) -> list[tuple]:
        """
        Получает список всех вакансий,
        в названии которых содержатся переданные в метод слова, например python
        """
        conn = self.conn
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT * FROM vacancies WHERE name ILIKE %s
                """,
                ("%" + word + "%",),
            )
            result = cur.fetchall()
            conn.commit()
        conn.close()
        return result
