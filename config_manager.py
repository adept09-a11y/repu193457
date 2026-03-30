"""
config_manager.py - Управление конфигурацией приложения

Модуль для загрузки, сохранения и управления настройками приложения.
Конфигурация хранится в JSON файле, токены загружаются из .env файла.
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv


class ConfigManager:
    """
    Менеджер конфигурации приложения.
    
    Атрибуты:
        config_path (Path): Путь к файлу конфигурации
        config (dict): Словарь с текущей конфигурацией
        discord_token (str): Токен Discord
        telegram_token (str): Токен Telegram бота
    """
    
    def __init__(self, config_path: str = "config.json"):
        """
        Инициализация менеджера конфигурации.
        
        Args:
            config_path: Путь к файлу конфигурации JSON
        """
        self.config_path = Path(config_path)
        self.config = {}
        self.discord_token = ""
        self.telegram_token = ""
        
        # Загрузка переменных окружения из .env файла
        load_dotenv()
        
        # Загрузка токенов из переменных окружения
        self.discord_token = os.getenv("DISCORD_TOKEN", "")
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        
        # Загрузка или создание конфигурации
        self.load_config()
    
    def load_config(self) -> dict:
        """
        Загрузка конфигурации из файла.
        
        Если файл не существует, создается конфигурация по умолчанию.
        
        Returns:
            dict: Словарь с конфигурацией
        """
        default_config = {
            "telegram_chat_id": "",
            "tracked_users": [],
            "tracked_guilds": [],
            "filter_enabled": False,
            "keywords": []
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                # Добавляем отсутствующие ключи со значениями по умолчанию
                for key, value in default_config.items():
                    if key not in self.config:
                        self.config[key] = value
            except (json.JSONDecodeError, IOError) as e:
                print(f"Ошибка загрузки конфигурации: {e}")
                self.config = default_config.copy()
        else:
            self.config = default_config.copy()
            self.save_config()
        
        return self.config
    
    def save_config(self) -> bool:
        """
        Сохранение конфигурации в файл.
        
        Returns:
            bool: True если успешно, False иначе
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Ошибка сохранения конфигурации: {e}")
            return False
    
    def get_telegram_chat_id(self) -> str:
        """Получение Telegram chat_id."""
        return self.config.get("telegram_chat_id", "")
    
    def set_telegram_chat_id(self, chat_id: str) -> None:
        """
        Установка Telegram chat_id.
        
        Args:
            chat_id: ID чата Telegram
        """
        self.config["telegram_chat_id"] = chat_id
    
    def get_tracked_users(self) -> list:
        """Получение списка отслеживаемых пользователей."""
        return self.config.get("tracked_users", [])
    
    def add_tracked_user(self, user_id: str) -> bool:
        """
        Добавление пользователя в список отслеживаемых.
        
        Args:
            user_id: Discord ID пользователя
            
        Returns:
            bool: True если добавлен, False если уже существует
        """
        user_id = str(user_id).strip()
        if user_id and user_id not in self.config.get("tracked_users", []):
            if "tracked_users" not in self.config:
                self.config["tracked_users"] = []
            self.config["tracked_users"].append(user_id)
            return True
        return False
    
    def remove_tracked_user(self, user_id: str) -> bool:
        """
        Удаление пользователя из списка отслеживаемых.
        
        Args:
            user_id: Discord ID пользователя
            
        Returns:
            bool: True если удален, False если не найден
        """
        user_id = str(user_id).strip()
        users = self.config.get("tracked_users", [])
        if user_id in users:
            users.remove(user_id)
            return True
        return False
    
    def get_tracked_guilds(self) -> list:
        """Получение списка отслеживаемых серверов."""
        return self.config.get("tracked_guilds", [])
    
    def add_tracked_guild(self, guild_id: str) -> bool:
        """
        Добавление сервера в список отслеживаемых.
        
        Args:
            guild_id: Discord ID сервера
            
        Returns:
            bool: True если добавлен, False если уже существует
        """
        guild_id = str(guild_id).strip()
        if guild_id and guild_id not in self.config.get("tracked_guilds", []):
            if "tracked_guilds" not in self.config:
                self.config["tracked_guilds"] = []
            self.config["tracked_guilds"].append(guild_id)
            return True
        return False
    
    def remove_tracked_guild(self, guild_id: str) -> bool:
        """
        Удаление сервера из списка отслеживаемых.
        
        Args:
            guild_id: Discord ID сервера
            
        Returns:
            bool: True если удален, False если не найден
        """
        guild_id = str(guild_id).strip()
        guilds = self.config.get("tracked_guilds", [])
        if guild_id in guilds:
            guilds.remove(guild_id)
            return True
        return False
    
    def is_filter_enabled(self) -> bool:
        """Проверка включен ли фильтр сообщений."""
        return self.config.get("filter_enabled", False)
    
    def set_filter_enabled(self, enabled: bool) -> None:
        """
        Включение/выключение фильтра сообщений.
        
        Args:
            enabled: True для включения, False для выключения
        """
        self.config["filter_enabled"] = enabled
    
    def get_keywords(self) -> list:
        """Получение списка ключевых слов для фильтра."""
        return self.config.get("keywords", [])
    
    def add_keyword(self, keyword: str) -> bool:
        """
        Добавление ключевого слова в фильтр.
        
        Args:
            keyword: Ключевое слово
            
        Returns:
            bool: True если добавлено, False если уже существует
        """
        keyword = str(keyword).strip().lower()  # Конвертируем в lowercase перед проверкой
        if keyword and keyword not in self.config.get("keywords", []):
            if "keywords" not in self.config:
                self.config["keywords"] = []
            self.config["keywords"].append(keyword)
            return True
        return False
    
    def remove_keyword(self, keyword: str) -> bool:
        """
        Удаление ключевого слова из фильтра.
        
        Args:
            keyword: Ключевое слово
            
        Returns:
            bool: True если удалено, False если не найдено
        """
        keyword = str(keyword).strip().lower()
        keywords = self.config.get("keywords", [])
        if keyword in keywords:
            keywords.remove(keyword)
            return True
        return False
    
    def should_forward_message(self, content: str, mentioned_user_ids: list, 
                               owner_id: str = None) -> bool:
        """
        Проверка должно ли сообщение быть переслано на основе фильтра.
        
        Args:
            content: Текст сообщения
            mentioned_user_ids: Список ID упомянутых пользователей
            owner_id: ID владельца (для проверки упоминания)
            
        Returns:
            bool: True если сообщение должно быть переслано
        """
        if not self.is_filter_enabled():
            return True
        
        content_lower = content.lower()
        
        # Проверка упоминания владельца
        if owner_id and str(owner_id) in mentioned_user_ids:
            return True
        
        # Проверка ключевых слов
        for keyword in self.get_keywords():
            if keyword in content_lower:
                return True
        
        return False
