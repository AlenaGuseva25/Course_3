import argparse
import requests
from typing import List
from src.interaction_API import HeadHunterAPI
from src.interaction_with_vacancies import DBManager, create_database
from src.utils import the_key_word


def user_interaction() -> None:
    """Функция для взаимодействия с пользователем и выполнения действий с базой данных"""
    key_word = the_key_word
    employers = list(HeadHunterAPI(key_word).get_employers())
    vacancies = list(HeadHunterAPI(key_word).get_vacancies_by_employers(employers))

    create_database()
    save_data_to_database(employers, vacancies)

    while True:
        print("\nКакое действие с базой данных хотите произвести?")
        print("1. Получить список всех компаний и количество вакансий у каждой компании.")
        print("2. Получить список всех вакансий.")
        print("3. Получить среднюю зарплату по вакансиям.")
        print("4. Получить список вакансий с зарплатой выше средней.")
        print("5. Получить список всех вакансий, в названии которых есть искомое слово.")
        print("6. Выход")

        user_choice = input("Выберите действие (1-6): ")

        if user_choice == '1':
            result = DBManager().get_companies_and_vacancies_count()
            print("Компании и количество вакансий:")
            for company, count in result:
                print(f"{company}: {count} вакансий")

        elif user_choice == '2':
            result = DBManager().get_all_vacancies()
            print("Все вакансии:")
            for vacancy in result:
                print(f"Вакансия: {vacancy[1]}, Зарплата: {vacancy[2]}, Работодатель: {vacancy[5]}")

        elif user_choice == '3':
            result = DBManager().get_avg_salary()
            print(f"Средняя зарплата по вакансиям: {result}")

        elif user_choice == '4':
            result = DBManager().get_vacancies_with_higher_salary()
            print("Вакансии с зарплатой выше средней:")
            for vacancy in result:
                print(f"Вакансия: {vacancy[1]}, Зарплата: {vacancy[2]}, Работодатель: {vacancy[5]}")

        elif user_choice == '5':
            keyword = input("Введите искомое слово: ")
            result = DBManager().get_vacancies_with_keyword(keyword)
            if result:
                print("Вакансии по ключевому слову:")
                for vacancy in result:
                    print(f"Вакансия: {vacancy[1]}, Зарплата: {vacancy[2]}, Работодатель: {vacancy[5]}")
            else:
                print("Нет вакансий по данному ключевому слову.")

        elif user_choice == '6':
            print("Выход из программы.")
            break

        else:
            print("Некорректный ввод. Пожалуйста, выберите действие от 1 до 6.")


# Запуск функции взаимодействия с пользователем
if __name__ == "__main__":
    user_interaction()





