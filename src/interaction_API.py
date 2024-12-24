import abc
import requests
import json
from typing import List, Dict, Any
from src.utils import validate_vacancy


class BaseAPI(abc.ABC):
    """Абстрактный класс для АПИ"""

    def __init__(self, base_url: str, headers: dict):
        self._BASE_URL = base_url
        self._headers = headers

    @abc.abstractmethod
    def _make_request(self, url: str, params: Dict = None) -> requests.Response:
        """Абстрактный метод для запросов к АПИ"""
        pass


class HeadHunterAPI(BaseAPI):
    """Класс для работы с API HeadHunter."""

    def __init__(self, base_url: str, headers: dict, per_page: int = 100):
        super().__init__(base_url, headers)
        self._per_page = per_page


    def _make_request(self, url: str, params: dict = None) -> requests.Response:
         """Выполняет запрос к API, обрабатывает ошибки и возвращает ответ."""
         try:
            response = requests.get(url, headers=self._headers, params=params)
            response.raise_for_status()
            return response
         except requests.exceptions.RequestException as e:
            print(f"Ошибка сети: {e}")
            raise
         except json.JSONDecodeError as e:
            print(f"Ошибка декодирования JSON: {e}")
            raise
         except KeyError as e:
            print(f"Ошибка: ключ не найден: {e}")
            raise



    def get_employers(self, only_with_vacancies: bool = True, top_n: int = 10) -> List[Dict[str, Any]]:
        """Получает список компаний с вакансиями."""
        employers_url = f"{self._BASE_URL}/employers"
        params = {"only_with_vacancies": only_with_vacancies}

        response = self._make_request(employers_url, params=params)
        data = response.json()
        employers = data.get("items", [])

        if not employers:
            print("Нет работодателей в ответе")
            return []
        return employers[:top_n]


    def get_vacancies_by_employers(self, employers: list) -> List[Dict[str, Any]]:
       """Получает вакансии для списка компаний."""
       all_vacancies = []
       for employer in employers:
          employer_id = employer.get("id")
          if employer_id is None:
                print("ID компании не найден.")
                continue

          vacancies_url = f"{self._BASE_URL}/vacancies"
          params = {"employer_id": employer_id}

          try:
            response = self._make_request(vacancies_url, params=params)
            data = response.json()
            vacancies = data.get("items", [])
            for vacancy in vacancies:
                if validate_vacancy(vacancy):
                    all_vacancies.append(vacancy)
          except Exception as e:
             print(f"Ошибка при получении вакансий для компании {employer_id}: {e}")
             continue
       return all_vacancies


