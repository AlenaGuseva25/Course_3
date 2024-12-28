import abc
import requests
from typing import List, Dict, Any, Optional


class BaseAPI(abc.ABC):
    """Абстрактный класс для АПИ"""

    def __init__(self, base_url: str, headers: dict):
        self._BASE_URL = base_url
        self._headers = headers

    @abc.abstractmethod
    def _make_request(self, url: str, params: Dict = None) -> requests.Response:
        """Абстрактный метод для запросов к АПИ"""
        pass


class HeadHunterAPI:
    """Класс для работы с API HeadHunter."""

    def __init__(self, base_url: str, headers: Dict[str, str]):
        """Инициализация класса HeadHunterAPI."""
        self.base_url = base_url
        self.headers = headers

    def _make_request(self, url: str, params: Dict = None) -> Optional[requests.Response]:
        """Выполняет запрос к API."""
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return None

    def get_employers(self, only_with_vacancies: bool = True, top_n: int = 10) -> List[Dict[str, Any]]:
        """Получает список компаний с вакансиями."""
        employers_url = f"{self.base_url}/employers"
        params = {"only_with_vacancies": only_with_vacancies}

        response = self._make_request(employers_url, params=params)
        if response:
            data = response.json()
            employers = data.get("items", [])
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
                vacancies_url = f"{self.base_url}/vacancies"
                params = {'employer_id': employer_id}
                response = self._make_request(vacancies_url, params=params)
                if response:
                    data = response.json()
                    items = data.get("items", [])
                    for item in items:
                        item["employer"] = employer
                    vacancies.extend(items)
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


