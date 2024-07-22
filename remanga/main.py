import sys
import winreg
import requests
import libs.remangaAPI
import asyncio
import aiohttp
import json
from typing import List, Dict


class ReManga:
    API_URL = "https://api.remanga.org/api"

    API_PATH: dict = {
        "login": "/users/login/",
        "views": "/activity/views/",
        "inventory": "/inventory/{}",
        "catalog": "/search/catalog",
        "chapters": "/titles/chapters",
        "current": "/v2/users/current",
        "bookmarks": "/users/{}/bookmarks",
        "merge_cards": "/inventory/{}/cards/merge/",
        "count_bookmarks": "/users/{}/user_bookmarks",
    }

    SITE_URL = "https://remanga.org"

    SITE_PATHS: dict = {
        "node": "/node-api/cookie/",
        "manga_page": "/_next/data/0WMsTVhcJNvltEilcpQjj/ru/manga/{}.json",
    }
    DATA_DIR = "data"
    CACHE_PATH = "data/{}_cache.json"

    @classmethod
    async def login(cls, session, account: Dict[str, str]):
        """
        Асинхронная функция для авторизации аккаунта.

        Аргументы:
        - session: Экземпляр aiohttp.ClientSession для выполнения запросов.
        - account (Dict[str, str]): Словарь с данными аккаунта.
        """
        url = cls.API_URL + cls.API_PATH["login"]
        credentials = {"login": account["login"], "password": account["password"]}
        async with session.post(url, json=credentials) as response:
            return await response.json()


def read_accounts_safe(file_path="accounts.txt"):
    """
    Функция для чтения данных аккаунтов из файла. Данные могут быть в формате login:password или login:password:token.
    Если токен отсутствует, он оставляется пустым.

    Аргументы:
    - file_path (str): Путь к файлу с данными аккаунтов, относительно main.py или абсолютный путь.

    Возвращает:
    - List[Dict[str, str]]: Список словарей, где каждый словарь содержит информацию об аккаунте ('login', 'password', и, опционально, 'token').
    """
    accounts = []  # Инициализация списка для хранения данных аккаунтов
    try:
        with open(file_path, "r") as file:  # Открытие файла для чтения
            for line in file:  # Перебор каждой строки в файле
                line = (
                    line.strip()
                )  # Удаление пробельных символов и символов перевода строки
                if not line:  # Пропуск пустых строк
                    continue
                parts = line.split(":")  # Разбиение строки на части по символу ':'
                if (
                    len(parts) < 2
                ):  # Проверка на наличие минимально необходимых данных (логин и пароль)
                    print(
                        f"Неверные данные аккаунта, отсутствуют поля: {line}"
                    )  # Вывод сообщения об ошибке
                    continue
                account = {
                    "login": parts[0],  # Сохранение логина
                    "password": parts[1],  # Сохранение пароля
                    "token": (
                        parts[2] if len(parts) == 3 else ""
                    ),  # Сохранение токена, если он есть, иначе пустая строка
                }
                accounts.append(
                    account
                )  # Добавление словаря с данными аккаунта в список
    except FileNotFoundError as e:  # Обработка исключения, если файл не найден
        print(f"Ошибка: Файл с данными аккаунтов не найден {e}")
    except Exception as e:  # Обработка всех остальных исключений
        print(f"Произошла непредвиденная ошибка: {e}")
    return accounts  # Возврат списка аккаунтов


# Пример использования
accounts = read_accounts_safe()
print(accounts)


async def main():
    accounts = read_accounts_safe()  # Чтение аккаунтов из файла
    async with aiohttp.ClientSession() as session:
        tasks = [ReManga.login(session, account) for account in accounts]
        responses = await asyncio.gather(*tasks)
        for response in responses:
            print(response)  # Вывод ответа от сервера


# Запуск асинхронного кода
asyncio.run(main())
