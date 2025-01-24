import requests
from typing import List
from src.db_manager import DBManager, create_database, create_tables, save_data_to_db
from src.interaction_API import HeadHunterAPI


def main() -> list:
    """
    Главная функция для запуска работы всего проекта.
    """
    api = HeadHunterAPI()
    employers = api.get_employers(10)
    vacancies = api.get_vacancies_by_employers(employers)

    create_database()
    create_tables()
    save_data_to_db(employers, vacancies)
    db_manager = DBManager()

    result = []
    while True:
        user_choice = int(
            input(
                "Какое действие с базой данных хотите произвести?\n"
                "1. Получить список всех компаний и количество вакансий у каждой компании.\n"
                "2. Получить список всех вакансий.\n"
                "3. Получить среднюю зарплату по вакансиям.\n"
                "4. Получить список вакансий с зарплатой выше средней.\n"
                "5. Получить список всех вакансий, в названии которых есть искомое слово.\n"
                "6. Выход\n"
            )
        )

        if user_choice == 1:
            result = db_manager.get_companies_and_vacancies_count()
        elif user_choice == 2:
            result = db_manager.get_all_vacancies()
        elif user_choice == 3:
            result = db_manager.get_avg_salary()
        elif user_choice == 4:
            result = db_manager.get_vacancies_with_higher_salary()
        elif user_choice == 5:
            word = input("Введите слово для поиска в названиях вакансий: ")
            result = db_manager.get_vacancies_with_keyword(word)
            print("Результаты поиска по слову '{}':".format(word))
        elif user_choice == 6:
            print("Выход из программы.")
            break


        return result


if __name__ == "__main__":
    outcome = main()
    print(outcome)
