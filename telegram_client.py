"""
Клиент для отправки сообщений в Telegram.
"""

import logging
from typing import Optional

try:
    from telegram import Bot
    from telegram.error import TelegramError
except ImportError:
    raise ImportError("Необходимо установить python-telegram-bot: pip install python-telegram-bot")

from config_manager import config_manager, ConfigManager

logger = logging.getLogger(__name__)


class TelegramClient:
    """Класс для отправки сообщений в Telegram."""

    def __init__(self, config_mgr: ConfigManager):
        self.config_manager = config_mgr
        self.bot: Optional[Bot] = None
        self.chat_id: Optional[str] = None
        self._initialized = False

    def _ensure_initialized(self):
        """Убеждается, что бот инициализирован."""
        if not self._initialized:
            token = self.config_manager.get_telegram_token()
            self.chat_id = self.config_manager.get_telegram_chat_id()
            
            if not token:
                logger.error("Токен Telegram не найден!")
                return False
            
            if not self.chat_id:
                logger.error("Chat ID Telegram не указан!")
                return False
            
            try:
                self.bot = Bot(token=token)
                self._initialized = True
                logger.info("Telegram бот инициализирован")
                return True
            except Exception as e:
                logger.error(f"Ошибка инициализации Telegram бота: {e}")
                return False
        
        return True

    async def send_message(self, text: str, parse_mode: str = 'HTML') -> bool:
        """
        Отправляет сообщение в Telegram.
        
        Args:
            text: Текст сообщения
            parse_mode: Режим парсинга ('HTML' или 'Markdown')
            
        Returns:
            True если сообщение отправлено успешно
        """
        if not self._ensure_initialized():
            return False

        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode=parse_mode,
                disable_web_page_preview=False
            )
            logger.debug(f"Сообщение отправлено в Telegram (chat_id: {self.chat_id})")
            return True
        except TelegramError as e:
            logger.error(f"Ошибка Telegram API: {e}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при отправке в Telegram: {e}")
            return False

    async def test_connection(self) -> bool:
        """
        Проверяет соединение с Telegram.
        
        Returns:
            True если соединение успешно
        """
        if not self._ensure_initialized():
            return False

        try:
            # Получаем информацию о боте
            me = await self.bot.get_me()
            logger.info(f"Telegram бот: @{me.username} ({me.first_name})")
            
            # Отправляем тестовое сообщение
            await self.bot.send_message(
                chat_id=self.chat_id,
                text="✅ <b>Тестовое сообщение</b>\n\nСоединение с Telegram установлено успешно!",
                parse_mode='HTML'
            )
            logger.info("Тестовое сообщение отправлено")
            return True
        except TelegramError as e:
            logger.error(f"Ошибка подключения к Telegram: {e}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при тестировании: {e}")
            return False

    def update_chat_id(self, chat_id: str):
        """Обновляет Chat ID."""
        self.chat_id = chat_id
        self.config_manager.set_telegram_chat_id(chat_id)
        logger.info(f"Chat ID обновлен: {chat_id}")


# Глобальный экземпляр
telegram_client = TelegramClient(config_manager)
