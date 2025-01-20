import abc

import requests
from typing import List, Dict, Any, Optional


class BaseAPI(abc.ABC):
    """Абстрактный класс для АПИ"""

    def __init__(self):
        self._BASE_URL = 'https://api.hh.ru'
        self._headers = {"text": ""}
        self.params = {
            "text": '',
            "page": 0,
            "per_page": 10,
        }

    @abc.abstractmethod
    def _make_request(self, url: str, params: Dict = None) -> requests.Response:
        """Абстрактный метод для запросов к АПИ"""
        pass


class HeadHunterAPI(BaseAPI):
    """Класс для работы с API HeadHunter."""

    def __init__(self):
        """Инициализация класса HeadHunterAPI."""
        super().__init__()
        self.params = {"sort_by": "by_vacancies_open", "only_with_vacancies": "only_with_vacancies", "area": 113}
        # self.base_url = base_url
        # self.headers = headers

    def _make_request(self, url: str, params: Dict = None) -> Optional[requests.Response]:
        """Выполняет запрос к API."""
        params = self.params
        try:
            response = requests.get(url, headers=self._headers, params=params)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return None

    def get_employers(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """Получает список компаний с вакансиями."""
        employers_url = f"{self._BASE_URL}/employers"
        employers = []
        # params = {"only_with_vacancies": "true" if only_with_vacancies else "false"}

        response = self._make_request(employers_url, params=self.params)
        if response:
            data = response.json()["items"]
            for dat in data:
                employer = {"id": dat.get("id"),
                         "name": dat.get("name"),
                         "url": dat.get("url"),
                         "open vacancies": dat.get("open_vacancies")}
                employers.append(employer)
            # data.get("items", [])
            if not employers:
                print("Нет работодателей в ответе")
                return []
            return employers[:top_n]
        return []

    def get_vacancies_by_employers(self, employers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Получает список вакансий по списку работодателей."""
        vacancies = []
        for employer in employers:
            employer_id = employer.get("id")
            if employer_id:
                vacancies_url = f"{self._BASE_URL}/vacancies"
                params = {"page" : 0, "per_page": 20, "text": "", "employer_id": employer_id}
                response = self._make_request(vacancies_url, params=params)
                if response:
                    data = response.json()["items"]
                    for dat in data:
                        if dat["salary"] and dat["salary"]["currency"] == "RUR":
                            vacancy = {"id": dat.get("id"),
                                    "name": dat.get("name"),
                                    "url": dat.get("url"),
                                    "employer_id": dat.get("employer").get("id"),
                                    "salary": dat.get("salary")}
                            vacancies.append(vacancy)
        return vacancies

    # def get_vacancies_by_keyword(self, keyword: str, only_with_salary: bool = True) -> List[Dict[str, Any]]:
    #     """Получает список вакансий по ключевому слову."""
    #     vacancies_url = f"{self._BASE_URL}/vacancies"
    #     params = {"text": keyword}
    #
    #     response = self._make_request(vacancies_url, params=params)
    #     if response:
    #         data = response.json()
    #         items = data.get("items", [])
    #
    #         # Фильтруем вакансии по ключевому слову
    #         filtered_vacancies = [
    #             vacancy
    #             for vacancy in items
    #             if keyword.lower() in vacancy.get("name", "").lower()
    #         ]
    #
    #         if only_with_salary:
    #             # Дополнительная фильтрация по наличию зарплаты
    #             filtered_vacancies = [
    #                 vacancy for vacancy in filtered_vacancies if vacancy.get("salary") is not None
    #             ]
    #
    #         # Форматируем результат, чтобы включить только нужные поля
    #         formatted_vacancies = []
    #         for vacancy in filtered_vacancies:
    #             formatted_vacancy = {
    #                 "name": vacancy.get("name"),
    #                 "company": vacancy.get("employer", {}).get("name"),
    #                 "salary": self._format_salary(vacancy.get("salary")),
    #                 "url": vacancy.get("alternate_url"),
    #                 "description": vacancy.get("snippet", {}).get("responsibility", "")
    #             }
    #             formatted_vacancies.append(formatted_vacancy)
    #
    #         return formatted_vacancies
    #
    #     return []

    # def _format_salary(self, salary: Optional[Dict[str, Any]]) -> str:
    #     """Форматирует зарплату для удобного отображения."""
    #     if salary:
    #         salary_from = salary.get("from")
    #         salary_to = salary.get("to")
    #         currency = salary.get("currency")
    #
    #         salary_str = ""
    #         if salary_from and salary_to:
    #             salary_str = f"{salary_from} - {salary_to} {currency}"
    #         elif salary_from:
    #             salary_str = f"от {salary_from} {currency}"
    #         elif salary_to:
    #             salary_str = f"до {salary_to} {currency}"
    #         else:
    #             salary_str = "Не указана"
    #
    #         return salary_str
    #
    #     return "Не указана"


    def validate_vacancy(self, vacancy: Dict[str, Any]) -> bool:
        """Метод проверяет структуру данных вакансии."""
        return (
                vacancy.get("name") is not None
                and vacancy.get("area") is not None
                and vacancy.get("area", {}).get("name") is not None
                and vacancy.get("salary") is not None
                and vacancy["salary"].get("currency") == "RUR"
                and vacancy.get("alternate_url") is not None
                and vacancy.get("employer") is not None
                and vacancy["employer"].get("name") is not None
        )


result = HeadHunterAPI().get_employers(10)
print(result)

p = HeadHunterAPI().get_vacancies_by_employers(result)
print(p)