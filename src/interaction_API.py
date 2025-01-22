import abc
from typing import Any, Dict, List, Optional

import requests


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

    def __init__(self, key_word: str = ''):
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
        url = f"{self._BASE_URL}/vacancies"
        employer_ids = [employer.get("id") for employer in employers]

        for employer_id in employer_ids:
            self.params = {"page": 0, "per_page": 20, "text": "", "employer_id": employer_ids}

        while self.params.get("page") < 20:
            response = self._make_request(url, params=self.params)

            if response and response.status_code == 200:
                data = response.json().get("items", [])
                for dat in data:
                    if dat.get("employer") and dat["employer"].get("id") in employer_ids:
                        if dat["salary"] and dat["salary"]["currency"] == "RUR":
                            vacancy = {
                                "vacancy_id": dat.get("id"),
                                "name": dat.get("name"),
                                "salary": dat["salary"],
                                "url": dat.get("alternate_url"),
                                "employer_id": dat["employer"].get("id"),
                            }
                            if vacancy["vacancy_id"] not in vacancies:
                                vacancies.append(vacancy)

                self.params["page"] += 1
            else:
                break

        return vacancies


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


# result = HeadHunterAPI().get_employers(10)
# print(result)
#
# p = HeadHunterAPI().get_vacancies_by_employers(result)
# print(p)