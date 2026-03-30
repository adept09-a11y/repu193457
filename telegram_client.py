"""
telegram_client.py - Клиент для отправки сообщений в Telegram

Модуль для отправки уведомлений в Telegram через Bot API.
"""

import logging
from typing import Optional, List
from telegram import Bot
from telegram.error import TelegramError


logger = logging.getLogger(__name__)


class TelegramClient:
    """
    Клиент для отправки сообщений в Telegram.
    
    Атрибуты:
        bot_token (str): Токен Telegram бота
        chat_id (str): ID чата для отправки сообщений
        bot (Bot): Экземпляр бота Telegram
    """
    
    def __init__(self, bot_token: str, chat_id: str):
        """
        Инициализация Telegram клиента.
        
        Args:
            bot_token: Токен Telegram бота
            chat_id: ID чата для отправки сообщений
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.bot: Optional[Bot] = None
        
        if bot_token:
            self._initialize_bot()
    
    def _initialize_bot(self) -> None:
        """Инициализация бота Telegram."""
        try:
            self.bot = Bot(token=self.bot_token)
            logger.info("Telegram бот инициализирован")
        except Exception as e:
            logger.error(f"Ошибка инициализации Telegram бота: {e}")
            self.bot = None
    
    def set_chat_id(self, chat_id: str) -> None:
        """
        Установка ID чата для отправки сообщений.
        
        Args:
            chat_id: ID чата Telegram
        """
        self.chat_id = chat_id
        logger.info(f"Telegram chat_id установлен: {chat_id}")
    
    def update_bot_token(self, bot_token: str) -> bool:
        """
        Обновление токена бота.
        
        Args:
            bot_token: Новый токен Telegram бота
            
        Returns:
            bool: True если успешно
        """
        self.bot_token = bot_token
        try:
            self.bot = Bot(token=bot_token)
            logger.info("Токен Telegram бота обновлен")
            return True
        except Exception as e:
            logger.error(f"Ошибка обновления токена Telegram бота: {e}")
            self.bot = None
            return False
    
    async def send_message(self, message: str, 
                          parse_mode: str = None,
                          disable_notification: bool = False) -> bool:
        """
        Отправка текстового сообщения в Telegram.
        
        Args:
            message: Текст сообщения
            parse_mode: Режим парсинга (Markdown, HTML, etc.)
            disable_notification: Отправить без звука
            
        Returns:
            bool: True если успешно отправлено
        """
        if not self.bot or not self.chat_id:
            logger.error("Telegram бот не инициализирован или chat_id не установлен")
            return False
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode,
                disable_notification=disable_notification
            )
            logger.debug(f"Сообщение отправлено в Telegram: {message[:50]}...")
            return True
        except TelegramError as e:
            logger.error(f"Ошибка отправки сообщения в Telegram: {e}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при отправке в Telegram: {e}")
            return False
    
    async def send_notification(self, 
                               timestamp: str,
                               guild_name: str,
                               channel_name: str,
                               author_name: str,
                               author_id: str,
                               content: str,
                               message_url: str,
                               attachments: List[str] = None) -> bool:
        """
        Отправка форматированного уведомления о сообщении Discord.
        
        Args:
            timestamp: Время сообщения
            guild_name: Название сервера
            channel_name: Название канала
            author_name: Имя автора
            author_id: ID автора
            content: Текст сообщения
            message_url: Ссылка на сообщение
            attachments: Список ссылок на вложения
            
        Returns:
            bool: True если успешно отправлено
        """
        # Форматирование сообщения
        message = (
            f"🔔 <b>Новое сообщение</b>\n\n"
            f"📅 <b>Время:</b> {timestamp}\n"
            f"🏷 <b>Сервер:</b> {guild_name}\n"
            f"📺 <b>Канал:</b> {channel_name}\n"
            f"👤 <b>Автор:</b> {author_name} ({author_id})\n"
            f"💬 <b>Сообщение:</b>\n{content}\n\n"
            f"🔗 <a href=\"{message_url}\">Открыть сообщение</a>"
        )
        
        # Добавление вложений
        if attachments:
            message += "\n\n📎 <b>Вложения:</b>\n"
            for i, attachment in enumerate(attachments, 1):
                message += f"{i}. {attachment}\n"
        
        # Ограничение длины сообщения (Telegram limit ~4096 символов)
        if len(message) > 4000:
            message = message[:4000] + "\n\n... (сообщение обрезано)"
        
        success = await self.send_message(message, parse_mode="HTML")
        
        if not success:
            logger.warning("Не удалось отправить уведомление в Telegram")
        
        return success
    
    async def send_log_message(self, log_text: str) -> bool:
        """
        Отправка логов в Telegram (для отладки).
        
        Args:
            log_text: Текст логов
            
        Returns:
            bool: True если успешно
        """
        # Экранирование HTML тегов в логах
        log_text = log_text.replace("<", "&lt;").replace(">", "&gt;")
        
        message = f"📋 <b>Лог приложения:</b>\n\n<pre>{log_text}</pre>"
        
        if len(message) > 4000:
            message = message[:4000] + "\n\n... (лог обрезан)"
        
        return await self.send_message(message, parse_mode="HTML")
    
    async def test_connection(self) -> bool:
        """
        Проверка соединения с Telegram API.
        
        Returns:
            bool: True если соединение успешно
        """
        if not self.bot:
            logger.error("Telegram бот не инициализирован")
            return False
        
        try:
            # Получение информации о боте
            me = await self.bot.get_me()
            logger.info(f"Подключение к Telegram успешно: @{me.username}")
            
            # Пробная отправка сообщения
            if self.chat_id:
                await self.send_message("✅ Подключение к Telegram успешно!")
            
            return True
        except TelegramError as e:
            logger.error(f"Ошибка подключения к Telegram: {e}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при проверке подключения: {e}")
            return False
