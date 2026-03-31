"""
Менеджер конфигурации приложения.
Управляет настройками в config.json и .env файлах.
"""

import json
import os
import logging
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('log.txt', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class ConfigManager:
    """Класс для управления конфигурацией приложения."""

    def __init__(self, config_path: str = 'config.json'):
        self.config_path = config_path
        self.config = {}
        self.load_config()

    def load_config(self):
        """Загружает конфигурацию из файла."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                logger.info(f"Конфигурация загружена из {self.config_path}")
            except Exception as e:
                logger.error(f"Ошибка загрузки конфигурации: {e}")
                self.config = {}
        else:
            self.config = {}
            logger.info("Создана новая конфигурация")

    def save_config(self):
        """Сохраняет конфигурацию в файл."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info(f"Конфигурация сохранена в {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения конфигурации: {e}")
            return False

    # === Discord Token ===
    def get_discord_token(self) -> Optional[str]:
        """Получает токен Discord из .env"""
        load_dotenv()
        return os.getenv('DISCORD_TOKEN')

    def set_discord_token(self, token: str):
        """Устанавливает токен Discord в .env"""
        self._update_env_file('DISCORD_TOKEN', token)

    # === Telegram Token ===
    def get_telegram_token(self) -> Optional[str]:
        """Получает токен Telegram бота из .env"""
        load_dotenv()
        return os.getenv('TELEGRAM_BOT_TOKEN')

    def set_telegram_token(self, token: str):
        """Устанавливает токен Telegram бота в .env"""
        self._update_env_file('TELEGRAM_BOT_TOKEN', token)

    def _update_env_file(self, key: str, value: str):
        """Обновляет переменную в .env файле."""
        env_path = Path('.env')
        lines = []
        
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        
        # Ищем существующую запись или добавляем новую
        found = False
        for i, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[i] = f"{key}={value}\n"
                found = True
                break
        
        if not found:
            lines.append(f"{key}={value}\n")
        
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        # Перезагружаем переменные окружения
        load_dotenv(override=True)
        logger.info(f"Обновлена переменная {key} в .env")

    # === Telegram Chat ID ===
    def get_telegram_chat_id(self) -> str:
        """Получает Chat ID для отправки уведомлений."""
        return self.config.get('telegram_chat_id', '')

    def set_telegram_chat_id(self, chat_id: str):
        """Устанавливает Chat ID."""
        self.config['telegram_chat_id'] = chat_id
        self.save_config()

    # === Discord Owner ID ===
    def get_discord_owner_id(self) -> str:
        """Получает ID владельца Discord."""
        return self.config.get('discord_owner_id', '')

    def set_discord_owner_id(self, owner_id: str):
        """Устанавливает ID владельца Discord."""
        self.config['discord_owner_id'] = owner_id
        self.save_config()

    # === Tracked Users ===
    def get_tracked_users(self) -> List[str]:
        """Получает список отслеживаемых пользователей."""
        return self.config.get('tracked_users', [])

    def add_tracked_user(self, user_id: str) -> bool:
        """Добавляет пользователя в список отслеживаемых."""
        users = self.get_tracked_users()
        if user_id not in users:
            users.append(user_id)
            self.config['tracked_users'] = users
            return self.save_config()
        return False

    def remove_tracked_user(self, user_id: str) -> bool:
        """Удаляет пользователя из списка отслеживаемых."""
        users = self.get_tracked_users()
        if user_id in users:
            users.remove(user_id)
            self.config['tracked_users'] = users
            return self.save_config()
        return False

    # === Tracked Guilds ===
    def get_tracked_guilds(self) -> List[str]:
        """Получает список отслеживаемых серверов."""
        return self.config.get('tracked_guilds', [])

    def add_tracked_guild(self, guild_id: str) -> bool:
        """Добавляет сервер в список отслеживаемых."""
        guilds = self.get_tracked_guilds()
        if guild_id not in guilds:
            guilds.append(guild_id)
            self.config['tracked_guilds'] = guilds
            return self.save_config()
        return False

    def remove_tracked_guild(self, guild_id: str) -> bool:
        """Удаляет сервер из списка отслеживаемых."""
        guilds = self.get_tracked_guilds()
        if guild_id in guilds:
            guilds.remove(guild_id)
            self.config['tracked_guilds'] = guilds
            return self.save_config()
        return False

    # === Filters ===
    def get_mention_filter(self) -> bool:
        """Проверяет, включен ли фильтр упоминаний."""
        return self.config.get('filter_mentions_only', False)

    def set_mention_filter(self, enabled: bool):
        """Включает/выключает фильтр упоминаний."""
        self.config['filter_mentions_only'] = enabled
        self.save_config()

    def get_keywords(self) -> List[str]:
        """Получает список ключевых слов."""
        return self.config.get('filter_keywords', [])

    def add_keyword(self, keyword: str) -> bool:
        """Добавляет ключевое слово."""
        keywords = self.get_keywords()
        if keyword and keyword not in keywords:
            keywords.append(keyword)
            self.config['filter_keywords'] = keywords
            return self.save_config()
        return False

    def remove_keyword(self, keyword: str) -> bool:
        """Удаляет ключевое слово."""
        keywords = self.get_keywords()
        if keyword in keywords:
            keywords.remove(keyword)
            self.config['filter_keywords'] = keywords
            return self.save_config()
        return False

    def get_track_voice_events(self) -> bool:
        """Проверяет, включено ли отслеживание голосовых событий."""
        return self.config.get('track_voice_events', True)

    def set_track_voice_events(self, enabled: bool):
        """Включает/выключает отслеживание голосовых событий."""
        self.config['track_voice_events'] = enabled
        self.save_config()


# Глобальный экземпляр
config_manager = ConfigManager()
