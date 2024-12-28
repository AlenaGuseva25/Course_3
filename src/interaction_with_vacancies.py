import os
import psycopg2
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional


class DBManager:
    """Класс для работы с базой данных."""

    def __init__(self):
        """Инициализация класса DBManager."""
        load_dotenv()
        self.host = os.getenv("DATABASE_HOST") or "localhost"
        self.port = os.getenv("DATABASE_PORT") or "5432"
        self.user = os.getenv("DATABASE_USER") or "postgres"
        self.password = os.getenv("DATABASE_PASSWORD")
        self.database = os.getenv("DATABASE_NAME") or "vacancies"
        self.conn = None

    def _connect(self) -> psycopg2.extensions.connection:
        """Устанавливает соединение с базой данных."""
        if not self.conn or self.conn.closed:
            try:
                self.conn = psycopg2.connect(
                    host=self.host, port=self.port, user=self.user, password=self.password, database=self.database,
                    client_encoding='utf-8'
                )
                self.conn.autocommit = True
                print("Соединение с БД установлено")
            except psycopg2.Error as e:
                print(f"Ошибка подключения к базе данных: {e}")
                raise
        return self.conn

    def close(self) -> None:
        """Закрывает соединение с базой данных."""
        if self.conn:
            self.conn.close()
            print("Соединение с БД закрыто")

    def create_database(self) -> None:
        """Создает базу данных, если она не существует."""
        temp_conn = None
        try:
            # Подключаемся к стандартной базе данных postgres
            temp_conn = psycopg2.connect(
                host=self.host, port=self.port, user=self.user, password=self.password, database="postgres"
            )
            temp_conn.autocommit = True
            with temp_conn.cursor() as cur:
                # Проверяем, существует ли база данных
                cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.database,))
                exists = cur.fetchone()

                if not exists:
                    cur.execute(f"CREATE DATABASE {self.database}")
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
                    name VARCHAR(255) NOT NULL
                    )
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS vacancies (
                    vacancy_id SERIAL PRIMARY KEY,
                    organization_id INT NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    salary VARCHAR(100),
                    url TEXT NOT NULL,
                    description TEXT,
                    FOREIGN KEY (organization_id) REFERENCES organizations (organization_id)
                    )
                """)
            print("Таблицы organizations и vacancies успешно созданы.")
        except psycopg2.Error as e:
            print(f"Ошибка при создании таблиц: {e}")
        finally:
            self.close()

    def insert_employers(self, employers: List[Dict[str, Any]]) -> None:
        """Добавляет работодателей в таблицу organizations."""
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                for employer in employers:
                    name_employer = employer.get("name")
                    if name_employer:
                        cur.execute(
                            "INSERT INTO organizations (name) VALUES (%s) RETURNING organization_id",
                            (name_employer,)
                        )
                        organization_id = cur.fetchone()[0]
                        employer["organization_id"] = organization_id
                    else:
                        print("Имя работодателя не найдено.")
            print("Работодатели добавлены в таблицу organizations")
        except psycopg2.Error as e:
            print(f"Ошибка при добавлении работодателей в таблицу organizations: {e}")
        finally:
            self.close()

    def insert_vacancies(self, vacancies: List[Dict[str, Any]]) -> None:
        """Вставляет данные о вакансиях в таблицу vacancies."""
        try:
            sql = """
               INSERT INTO vacancies (organization_id, name, salary, url, description)
                VALUES (%s, %s, %s, %s, %s)
            """
            for vacancy in vacancies:
              print(f"Inserting vacancy: {vacancy}") # Выводим данные перед преобразованием
              organization_id = vacancy['employer'].get('id')
              name = vacancy.get('name')
              salary = vacancy.get('salary')
              url = vacancy.get('alternate_url')
              description = vacancy.get('snippet', {}).get('requirement')
              if salary:
                    salary = f"{salary.get('from', '')} - {salary.get('to', '')} {salary.get('currency', '')}"
              vacancy_tuple = (organization_id, name, salary, url, description)
              self.cursor.execute(sql, vacancy_tuple)
            self.conn.commit()
            print("Данные о вакансиях успешно добавлены в таблицу vacancies.")
        except Exception as e:
            print(f"Ошибка при добавлении вакансий в таблицу vacancies: {e}")

    def get_companies_and_vacancies_count(self) -> List[tuple]:
        """Получает список всех компаний и количества вакансий у каждой компании."""
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT o.name, COUNT(v.vacancy_id)
                    FROM organizations o
                    LEFT JOIN vacancies v ON o.organization_id = v.organization_id
                    GROUP BY o.name
                """)
                result = cur.fetchall()
                return result
        except psycopg2.Error as e:
             print(f"Ошибка при запросе get_companies_and_vacancies_count: {e}")
             return []
        finally:
             self.close()

    def get_all_vacancies(self) -> List[tuple]:
        """Получает список всех вакансий с указанием названия компании, названия вакансии, зарплаты и ссылки на вакансию."""
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT o.name, v.name, v.salary, v.url
                    FROM vacancies v
                    LEFT JOIN organizations o ON v.organization_id = o.organization_id
                """)
                result = cur.fetchall()
                return result
        except psycopg2.Error as e:
            print(f"Ошибка при запросе get_all_vacancies: {e}")
            return []
        finally:
            self.close()


    def get_avg_salary(self) -> Optional[float]:
        """Получает среднюю зарплату по вакансиям."""
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT AVG(CAST(REPLACE(salary, ',', '.') AS DECIMAL))
                    FROM vacancies
                    WHERE salary != '' AND salary IS NOT NULL
                """)
                result = cur.fetchone()[0]
                return float(result) if result else None
        except psycopg2.Error as e:
            print(f"Ошибка при запросе get_avg_salary: {e}")
            return None
        finally:
            self.close()

    def get_vacancies_with_higher_salary(self) -> List[tuple]:
        """Получает список вакансий с зарплатой выше средней."""
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT o.name, v.name, v.salary, v.url
                    FROM vacancies v
                    LEFT JOIN organizations o ON v.organization_id = o.organization_id
                    WHERE CAST(REPLACE(v.salary, ',', '.') AS DECIMAL) > (
                    SELECT AVG(CAST(REPLACE(salary, ',', '.') AS DECIMAL))
                    FROM vacancies
                    WHERE salary != '' AND salary IS NOT NULL
                )
                """)
                result = cur.fetchall()
                return result
        except psycopg2.Error as e:
            print(f"Ошибка при запросе get_vacancies_with_higher_salary: {e}")
            return []
        finally:
            self.close()

    def get_vacancies_by_keyword(self, keyword: str) -> List[tuple]:
        """Получает список вакансий, в названии которых содержатся переданные в метод слова."""
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT o.name, v.name, v.salary, v.url
                    FROM vacancies v
                    LEFT JOIN organizations o ON v.organization_id = o.organization_id
                    WHERE v.name LIKE %s
                """, (f"%{keyword}%",))
                result = cur.fetchall()
                return result
        except psycopg2.Error as e:
            print(f"Ошибка при запросе get_vacancies_by_keyword: {e}")
            return []
        finally:
            self.close()