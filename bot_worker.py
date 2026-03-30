"""
bot_worker.py - Логика Discord бота (Userbot)

Модуль для подключения к Discord, прослушивания событий
и пересылки сообщений в Telegram.
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, Callable, Any

import discord
from discord.ext import commands

from config_manager import ConfigManager
from telegram_client import TelegramClient


logger = logging.getLogger(__name__)


class BotWorker:
    """
    Рабочий модуль Discord бота.
    
    Обрабатывает подключение к Discord, прослушивает события сообщений
    и пересылает уведомления в Telegram.
    
    Атрибуты:
        config_manager (ConfigManager): Менеджер конфигурации
        telegram_client (TelegramClient): Клиент Telegram
        client (commands.Bot): Экземпляр Discord клиента
        is_running (bool): Флаг работы бота
        on_status_change (Callable): Callback для изменения статуса
    """
    
    def __init__(self, config_manager: ConfigManager, telegram_client: TelegramClient):
        """
        Инициализация рабочего модуля бота.
        
        Args:
            config_manager: Менеджер конфигурации
            telegram_client: Клиент для отправки в Telegram
        """
        self.config_manager = config_manager
        self.telegram_client = telegram_client
        self.client: Optional[commands.Bot] = None
        self.is_running = False
        self.on_status_change: Optional[Callable[[str], None]] = None
        self.owner_id: Optional[str] = None
        
        # Для discord.py-self intents настраиваются автоматически
        # Но мы можем их указать явно при создании клиента
    
    def _setup_client(self) -> None:
        """Настройка Discord клиента."""
        if not self.config_manager.discord_token:
            logger.error("Discord токен не найден")
            raise ValueError("Discord токен не найден в .env файле")
        
        # Создание клиента с нужными интентами
        # discord.py-self автоматически настраивает все необходимые intents
        self.client = commands.Bot(
            command_prefix='!',
            case_insensitive=True
        )
        
        # Сохранение ID владельца (текущий пользователь)
        self.owner_id = None  # Будет установлен при подключении
        
        # Регистрация событий
        @self.client.event
        async def on_ready():
            await self._on_ready()
        
        @self.client.event
        async def on_message(message):
            await self._on_message(message)
        
        @self.client.event
        async def on_message_edit(before, after):
            await self._on_message_edit(before, after)
        
        @self.client.event
        async def on_voice_state_update(member, before, after):
            await self._on_voice_state_update(member, before, after)
        
        logger.info("Discord клиент настроен")
    
    async def _on_ready(self):
        """Обработчик события готовности клиента."""
        try:
            user = self.client.user
            self.owner_id = str(user.id)
            
            logger.info(f"Подключено как {user.name}#{user.discriminator} ({user.id})")
            
            if self.on_status_change:
                self.on_status_change(f"Connected as {user.name}")
            
            # Вывод отслеживаемых серверов
            tracked_guilds = self.config_manager.get_tracked_guilds()
            guild_count = len([g for g in self.client.guilds if str(g.id) in tracked_guilds])
            logger.info(f"Отслеживается {guild_count} из {len(tracked_guilds)} настроенных серверов")
            
        except Exception as e:
            logger.error(f"Ошибка в on_ready: {e}")
            if self.on_status_change:
                self.on_status_change(f"Error: {e}")
    
    async def _on_message(self, message):
        """
        Обработчик новых сообщений.
        
        Args:
            message: Сообщение Discord
        """
        try:
            # Игнорирование собственных сообщений
            if message.author.id == self.client.user.id:
                return
            
            # Проверка условий для пересылки
            if not self._should_forward(message):
                return
            
            # Отправка в Telegram
            await self._forward_to_telegram(message)
            
        except Exception as e:
            logger.error(f"Ошибка обработки сообщения: {e}")
    
    async def _on_message_edit(self, before, after):
        """
        Обработчик редактирования сообщений.
        
        Args:
            before: Сообщение до редактирования
            after: Сообщение после редактирования
        """
        try:
            # Игнорирование если контент не изменился
            if before.content == after.content:
                return
            
            # Игнорирование собственных сообщений
            if after.author.id == self.client.user.id:
                return
            
            # Проверка условий для пересылки
            if not self._should_forward(after):
                return
            
            # Отправка в Telegram с пометкой об редактировании
            await self._forward_to_telegram(after, is_edit=True)
            
        except Exception as e:
            logger.error(f"Ошибка обработки редактирования сообщения: {e}")
    
    async def _on_voice_state_update(self, member, before, after):
        """
        Обработчик изменения голосового состояния (подключение/отключение от голосового канала).
        
        Args:
            member: Участник Discord
            before: Состояние голосового канала до изменений
            after: Состояние голосового канала после изменений
        """
        try:
            # Игнорирование собственных событий
            if member.id == self.client.user.id:
                return
            
            member_id = str(member.id)
            tracked_users = self.config_manager.get_tracked_users()
            
            # Проверяем, отслеживается ли этот пользователь
            if tracked_users and member_id not in tracked_users:
                return
            
            # Определяем тип события
            joined_voice = False
            left_voice = False
            
            # Пользователь подключился к голосовому каналу
            if before.channel is None and after.channel is not None:
                joined_voice = True
            # Пользователь покинул голосовой канал
            elif before.channel is not None and after.channel is None:
                left_voice = True
            # Пользователь перешёл в другой канал (опционально можно обрабатывать)
            elif before.channel != after.channel and after.channel is not None:
                # Можно обработать как переход, но пока считаем за подключение к новому каналу
                joined_voice = True
            
            if not (joined_voice or left_voice):
                return
            
            # Получаем информацию о канале и сервере
            guild_name = "N/A"
            channel_name = "N/A"
            
            if after.channel:
                guild_name = after.channel.guild.name if after.channel.guild else "N/A"
                channel_name = after.channel.name if hasattr(after.channel, 'name') else str(after.channel.id)
            elif before.channel:
                guild_name = before.channel.guild.name if before.channel.guild else "N/A"
                channel_name = before.channel.name if hasattr(before.channel, 'name') else str(before.channel.id)
            
            # Форматирование имени пользователя
            discrim = member.discriminator
            if discrim == "0":
                user_name = member.name
            else:
                user_name = f"{member.name}#{discrim}"
            
            user_id = member_id
            
            # Формируем сообщение
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if joined_voice:
                action_text = f"🎤 Подключился к голосовому каналу"
            else:
                action_text = f"🔇 Покинул голосовой канал"
            
            content = f"{action_text}\nКанал: {channel_name}\nСервер: {guild_name}"
            
            # Отправка в Telegram
            success = await self.telegram_client.send_notification(
                timestamp=timestamp,
                guild_name=guild_name,
                channel_name=channel_name,
                author_name=user_name,
                author_id=user_id,
                content=content,
                message_url="N/A",
                attachments=None
            )
            
            if success:
                action = "подключился" if joined_voice else "отключился"
                logger.info(f"Пользователь {user_name} {action} от голосового канала")
            else:
                logger.warning(f"Не удалось отправить уведомление о голосовом событии")
                
        except Exception as e:
            logger.error(f"Ошибка обработки голосового события: {e}")
    
    def _should_forward(self, message) -> bool:
        """
        Проверка должно ли сообщение быть переслано.
        
        Args:
            message: Сообщение Discord
            
        Returns:
            bool: True если сообщение должно быть переслано
        """
        author_id = str(message.author.id)
        guild_id = str(message.guild.id) if message.guild else None
        
        # Получение списков отслеживания
        tracked_users = self.config_manager.get_tracked_users()
        tracked_guilds = self.config_manager.get_tracked_guilds()
        
        # Проверка сервера (если указан и есть в списке)
        if guild_id and tracked_guilds:
            if guild_id not in tracked_guilds:
                return False
        
        # Проверка пользователя (должен быть в списке отслеживаемых)
        if tracked_users:
            if author_id not in tracked_users:
                return False
        else:
            # Если список пустой, не пересылаем ничего
            return False
        
        # Проверка фильтра
        mentioned_ids = [str(user.id) for user in message.mentions]
        if not self.config_manager.should_forward_message(
            message.content or "", 
            mentioned_ids,
            self.owner_id
        ):
            return False
        
        return True
    
    async def _forward_to_telegram(self, message, is_edit: bool = False):
        """
        Пересылка сообщения в Telegram.
        
        Args:
            message: Сообщение Discord
            is_edit: True если сообщение отредактировано
        """
        try:
            # Сбор информации о сообщении
            timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
            guild_name = message.guild.name if message.guild else "Личное сообщение"
            channel_name = f"#{message.channel.name}" if hasattr(message.channel, 'name') else str(message.channel.id)
            
            # Форматирование имени автора
            author_discrim = message.author.discriminator
            if author_discrim == "0":  # Новые имена без дискриминатора
                author_name = message.author.name
            else:
                author_name = f"{message.author.name}#{author_discrim}"
            
            author_id = str(message.author.id)
            content = message.content or "[Нет текста]"
            
            # Ссылка на сообщение
            if message.guild and message.channel:
                message_url = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}"
            else:
                message_url = "N/A"
            
            # Вложения
            attachments = []
            for attachment in message.attachments:
                attachments.append(attachment.url)
            
            # Добавление пометки об редактировании
            if is_edit:
                content = f"[EDITED] {content}"
            
            # Отправка в Telegram
            success = await self.telegram_client.send_notification(
                timestamp=timestamp,
                guild_name=guild_name,
                channel_name=channel_name,
                author_name=author_name,
                author_id=author_id,
                content=content,
                message_url=message_url,
                attachments=attachments if attachments else None
            )
            
            if success:
                logger.info(f"Сообщение от {author_name} переслано в Telegram")
            else:
                logger.warning(f"Не удалось переслать сообщение в Telegram")
                
        except Exception as e:
            logger.error(f"Ошибка пересылки сообщения в Telegram: {e}")
    
    async def start(self):
        """Запуск бота."""
        if self.is_running:
            logger.warning("Бот уже запущен")
            return
        
        try:
            self._setup_client()
            self.is_running = True
            
            if self.on_status_change:
                self.on_status_change("Connecting...")
            
            logger.info("Запуск Discord бота...")
            await self.client.start(self.config_manager.discord_token, reconnect=True)
            
        except Exception as e:
            logger.error(f"Ошибка запуска бота: {e}")
            self.is_running = False
            if self.on_status_change:
                self.on_status_change(f"Error: {e}")
            raise
    
    async def stop(self):
        """Остановка бота."""
        if not self.is_running:
            return
        
        try:
            logger.info("Остановка Discord бота...")
            if self.client:
                await self.client.close()
            self.is_running = False
            
            if self.on_status_change:
                self.on_status_change("Stopped")
            
            logger.info("Discord бот остановлен")
            
        except Exception as e:
            logger.error(f"Ошибка остановки бота: {e}")
            if self.on_status_change:
                self.on_status_change(f"Stop error: {e}")
    
    def get_status(self) -> str:
        """Получение текущего статуса бота."""
        if not self.is_running:
            return "Stopped"
        if self.client and self.client.user:
            return f"Running as {self.client.user.name}"
        return "Running"
    
    def get_guild_info(self) -> list:
        """
        Получение информации о доступных серверах.
        
        Returns:
            list: Список кортежей (guild_id, guild_name)
        """
        if not self.client or not self.client.guilds:
            return []
        
        return [(str(guild.id), guild.name) for guild in self.client.guilds]
