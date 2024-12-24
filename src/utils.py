import json
from typing import Dict, Any


def validate_vacancy(vacancy: dict) -> bool:
    """Функция проверяет структуру данных вакансии."""
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