import json
from typing import Dict, List, Any, Optional


def read_json_file(filename: str) -> Optional[List[Dict[str, Any]]]:
    """Читает данные из JSON-файла."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Файл {filename} не найден.")
        return None
    except json.JSONDecodeError:
        print(f"Ошибка декодирования JSON в файле {filename}")
        return None


def write_json_file(filename: str, data: List[Dict[str, Any]]) -> bool:
    """Записывает данные в JSON-файл."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except IOError:
        print(f"Ошибка записи в файл {filename}")
        return False