import os
import psycopg2
from dotenv import load_dotenv
from typing import List, Any


def create_database(self) -> None:
    """Создает базу данных, если она не существует."""
    temp_conn = None
    try:
        temp_conn = self.conn
        temp_conn.autocommit = True
        with temp_conn.cursor() as cur:
            cur.execute(f"DROP DATABASE IF EXISTS {self.database}")
            cur.execute(f'CREATE DATABASE {self.database}')
            exists = cur.fetchone()
            print(f"База данных {self.database} успешно создана.")

    except psycopg2.Error as e:
        print(f"Не удалось создать базу данных {self.database}. Ошибка: {e}")

    finally:
        if temp_conn:
            temp_conn.close()


def create_tables(self) -> None:
    """Создает таблицы organizations и vacancies в БД."""
    conn = self._connect()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS organizations (
                organization_id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                url VARCHAR(255) NOT NULL,
                open_vacancies INTEGER NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS vacancies (
                vacancy_id SERIAL PRIMARY KEY,
                organization_id INT NOT NULL,
                name VARCHAR(255) NOT NULL,
                salary VARCHAR(100),
                url TEXT NOT NULL,
                FOREIGN KEY (organization_id) REFERENCES organizations (organization_id)
                )
            """)
            conn.commit()
        print("Таблицы organizations и vacancies успешно созданы.")
    except psycopg2.Error as e:
        print(f"Ошибка при создании таблиц: {e}")
    finally:
        self.close()


class DBManager:
    """Класс для работы с базой данных."""

    def __init__(self):
        """Инициализация класса DBManager."""
        load_dotenv()
        self.host = os.getenv("DATABASE_HOST")
        self.port = os.getenv("DATABASE_PORT")
        self.user = os.getenv("DATABASE_USER")
        self.password = os.getenv("DATABASE_PASSWORD")
        self.database = os.getenv("DATABASE_NAME")
        self.conn = psycopg2.connect(
                    host=self.host, port=self.port, user=self.user, password=self.password, database=self.database,
                    client_encoding='utf-8'
                )

    def _connect(self) -> psycopg2.extensions.connection:
        """Устанавливает соединение с базой данных."""
        if not self.conn or self.conn.closed:
            try:
                conn = self.conn
                print("Соединение с БД установлено")
            except psycopg2.Error as e:
                print(f"Ошибка подключения к базе данных: {e}")
                raise
        return self.conn

    def close(self) -> None:
        """Закрывает соединение с базой данных."""
        if self.conn:
            self.conn.commit()
            self.conn.close()
            print("Соединение с БД закрыто")


    def get_companies_and_vacancies_count(self) -> List[tuple]:
        """Получает список всех работодателей и количество вакансий у каждого работодателя"""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT e.name, COUNT(v.vacancies_id) 
                FROM employers e
                LEFT JOIN vacancies v ON e.id = v.employer_id 
                GROUP BY e.name
                """
            )
            result = cur.fetchall()
        return result

    def get_all_vacancies(self) -> Any:
        """Получает список всех вакансий с указанием названия работодателя,
        названия вакансии и зарплаты и ссылки на вакансию"""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT v.vacancies_id, v.name, v.salary_from, v.salary_to, v.vacancies_url, e.name AS employer_name
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.id
                """
            )
            total = cur.fetchall()
        return total

    def get_avg_salary(self) -> float:
        """Получает среднюю зарплату по вакансиям"""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT AVG((salary_from + salary_to) / 2) AS avg_salary FROM vacancies
                """
            )
            avg_salary = cur.fetchone()[0]
        return avg_salary

    def get_vacancies_with_higher_salary(self) -> List[tuple]:
        """Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям"""
        avg_salary = self.get_avg_salary()
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT v.*, e.name AS employer_name FROM vacancies v
                JOIN employers e ON v.employer_id = e.id
                WHERE (salary_to + salary_from) / 2 > %s
                """,
                [avg_salary],
            )
            vacancies = cur.fetchall()
        return vacancies

    def get_vacancies_with_keyword(self, word: str) -> List[tuple]:
        """Получает список всех вакансий, в названии которых содержатся переданные в метод слова"""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT v.*, e.name AS employer_name FROM vacancies v
                JOIN employers e ON v.employer_id = e.id
                WHERE v.name ILIKE %s
                """,
                ("%" + word + "%",),
            )
            result = cur.fetchall()
        return result

    def close(self):
        """Закрывает соединение с базой данных."""
        self.conn.close()


a = DBManager().create_database()
b = DBManager().create_tables()
