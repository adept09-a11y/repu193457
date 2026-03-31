"""
Модуль для работы с Discord Userbot.
Отслеживает сообщения и голосовые события, пересылает уведомления в Telegram.
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, List, Set

try:
    import discord
    from discord.ext import commands
except ImportError:
    raise ImportError("Необходимо установить discord.py-self: pip install 'discord.py-self>=1.9.2'")

from config_manager import ConfigManager
from telegram_client import TelegramClient

logger = logging.getLogger(__name__)


class DiscordUserbot:
    """Класс для управления Discord Userbot."""

    def __init__(self, config_manager: ConfigManager, telegram_client: TelegramClient):
        self.config_manager = config_manager
        self.telegram_client = telegram_client
        self.is_running = False
        self.client: Optional[commands.Bot] = None
        self.task: Optional[asyncio.Task] = None

        # Настройка интентов для userbot
        intents = discord.Intents.all()
        intents.message_content = True
        intents.members = True
        intents.presences = True
        
        self.intents = intents

    async def _run_bot(self):
        """Асинхронный запуск бота."""
        token = self.config_manager.get_discord_token()
        if not token:
            logger.error("Токен Discord не найден!")
            return

        try:
            # Создаем клиента с нужными интентами
            self.client = commands.Bot(
                command_prefix='!',
                intents=self.intents,
                case_insensitive=True
            )

            # Регистрируем события
            @self.client.event
            async def on_ready():
                logger.info(f"Userbot запущен как {self.client.user} (ID: {self.client.user.id})")
                self.is_running = True

            @self.client.event
            async def on_message(message):
                await self._handle_message(message)

            @self.client.event
            async def on_message_edit(before, after):
                await self._handle_message_edit(before, after)

            @self.client.event
            async def on_voice_state_update(member, before, after):
                await self._handle_voice_state_update(member, before, after)

            # Запускаем клиента
            await self.client.start(token, bot=False)

        except Exception as e:
            logger.error(f"Ошибка при запуске бота: {e}")
            self.is_running = False
            raise

    async def _handle_message(self, message):
        """Обработка нового сообщения."""
        if message.author == self.client.user:
            return  # Игнорируем свои сообщения

        # Проверяем фильтры
        if not self._should_forward_message(message):
            return

        # Формируем уведомление
        notification = self._format_message_notification(message)
        
        # Отправляем в Telegram
        await self._send_to_telegram(notification)

    async def _handle_message_edit(self, before, after):
        """Обработка редактирования сообщения."""
        if after.author == self.client.user:
            return

        if not self._should_forward_message(after):
            return

        # Проверяем, изменилось ли содержимое
        if before.content == after.content:
            return

        notification = self._format_message_edit_notification(before, after)
        await self._send_to_telegram(notification)

    async def _handle_voice_state_update(self, member, before, after):
        """Обработка изменений голосового состояния."""
        if member == self.client.user:
            return  # Игнорируем свои события

        # Проверяем, отслеживается ли пользователь
        tracked_users = self.config_manager.get_tracked_users()
        if str(member.id) not in tracked_users:
            return

        # Проверяем, отслеживается ли сервер (если есть список серверов)
        tracked_guilds = self.config_manager.get_tracked_guilds()
        if tracked_guilds and str(member.guild.id) not in tracked_guilds:
            return

        # Определяем тип события
        notification = None
        
        if after.channel and not before.channel:
            # Пользователь подключился к голосовому каналу
            notification = (
                f"🎤 <b>Подключился к голосовому каналу</b>\n\n"
                f"<b>Пользователь:</b> {member.display_name} ({member.id})\n"
                f"<b>Канал:</b> {after.channel.name}\n"
                f"<b>Сервер:</b> {member.guild.name}\n"
                f"<b>Время:</b> {datetime.now().strftime('%H:%M:%S')}"
            )
        elif before.channel and not after.channel:
            # Пользователь покинул голосовой канал
            notification = (
                f"🔇 <b>Покинул голосовой канал</b>\n\n"
                f"<b>Пользователь:</b> {member.display_name} ({member.id})\n"
                f"<b>Канал:</b> {before.channel.name}\n"
                f"<b>Сервер:</b> {member.guild.name}\n"
                f"<b>Время:</b> {datetime.now().strftime('%H:%M:%S')}"
            )
        elif before.channel and after.channel and before.channel != after.channel:
            # Пользователь перешел между каналами
            notification = (
                f"🔄 <b>Перешел в другой голосовой канал</b>\n\n"
                f"<b>Пользователь:</b> {member.display_name} ({member.id})\n"
                f"<b>С канала:</b> {before.channel.name}\n"
                f"<b>На канал:</b> {after.channel.name}\n"
                f"<b>Сервер:</b> {member.guild.name}\n"
                f"<b>Время:</b> {datetime.now().strftime('%H:%M:%S')}"
            )

        if notification:
            await self._send_to_telegram(notification)

    def _should_forward_message(self, message) -> bool:
        """Проверяет, нужно ли пересылать сообщение."""
        # Проверяем сервер
        tracked_guilds = self.config_manager.get_tracked_guilds()
        if tracked_guilds:
            if str(message.guild.id) not in tracked_guilds:
                return False

        # Проверяем пользователя
        tracked_users = self.config_manager.get_tracked_users()
        if str(message.author.id) not in tracked_users:
            return False

        # Проверяем фильтр по упоминаниям
        if self.config_manager.get_mention_filter():
            owner_id = self.config_manager.get_telegram_owner_id()
            if owner_id and f"<@{owner_id}>" not in message.content:
                return False

        # Проверяем фильтр по ключевым словам
        keywords = self.config_manager.get_keywords()
        if keywords:
            content_lower = message.content.lower()
            if not any(keyword.lower() in content_lower for keyword in keywords):
                return False

        return True

    def _format_message_notification(self, message) -> str:
        """Форматирует уведомление о новом сообщении."""
        time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        guild_name = message.guild.name if message.guild else "ЛС"
        channel_name = message.channel.name if hasattr(message.channel, 'name') else str(message.channel.id)
        
        author_discriminator = f"#{message.author.discriminator}" if message.author.discriminator != "0" else ""
        author_name = f"{message.author.name}{author_discriminator}"
        
        # Ссылка на сообщение
        message_link = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}" if message.guild else None
        
        notification = (
            f"💬 <b>Новое сообщение</b>\n\n"
            f"<b>Время:</b> {time_str}\n"
            f"<b>Сервер:</b> {guild_name}\n"
            f"<b>Канал:</b> {channel_name}\n"
            f"<b>Автор:</b> {author_name} ({message.author.id})\n"
        )
        
        if message.content:
            notification += f"\n<b>Текст:</b>\n{message.content[:1000]}"  # Ограничиваем длину
            
        if message.attachments:
            attachment_links = "\n".join([att.url for att in message.attachments[:5]])
            notification += f"\n\n<b>Вложения:</b>\n{attachment_links}"
            
        if message_link:
            notification += f"\n\n🔗 <a href='{message_link}'>Перейти к сообщению</a>"
            
        return notification

    def _format_message_edit_notification(self, before, after) -> str:
        """Форматирует уведомление об редактировании сообщения."""
        time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        guild_name = after.guild.name if after.guild else "ЛС"
        channel_name = after.channel.name if hasattr(after.channel, 'name') else str(after.channel.id)
        
        author_discriminator = f"#{after.author.discriminator}" if after.author.discriminator != "0" else ""
        author_name = f"{after.author.name}{author_discriminator}"
        
        message_link = f"https://discord.com/channels/{after.guild.id}/{after.channel.id}/{after.id}" if after.guild else None
        
        notification = (
            f"✏️ <b>Сообщение отредактировано</b>\n\n"
            f"<b>Время:</b> {time_str}\n"
            f"<b>Сервер:</b> {guild_name}\n"
            f"<b>Канал:</b> {channel_name}\n"
            f"<b>Автор:</b> {author_name} ({after.author.id})\n"
        )
        
        if before.content:
            notification += f"\n<b>Было:</b>\n{before.content[:500]}"
        if after.content:
            notification += f"\n\n<b>Стало:</b>\n{after.content[:500]}"
            
        if message_link:
            notification += f"\n\n🔗 <a href='{message_link}'>Перейти к сообщению</a>"
            
        return notification

    async def _send_to_telegram(self, text: str):
        """Отправляет уведомление в Telegram."""
        try:
            await self.telegram_client.send_message(text)
            logger.debug("Уведомление отправлено в Telegram")
        except Exception as e:
            logger.error(f"Ошибка отправки в Telegram: {e}")

    def start(self):
        """Запускает бота в отдельном потоке."""
        if self.is_running:
            logger.warning("Бот уже запущен!")
            return

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        self.task = loop.create_task(self._run_bot())
        
        def run_loop():
            try:
                loop.run_forever()
            except Exception as e:
                logger.error(f"Ошибка в цикле событий: {e}")
            finally:
                loop.close()

        import threading
        thread = threading.Thread(target=run_loop, daemon=True)
        thread.start()
        logger.info("Бот запущен в фоновом режиме")

    def stop(self):
        """Останавливает бота."""
        if not self.is_running or not self.client:
            logger.warning("Бот не запущен!")
            return

        try:
            if self.client.is_running():
                loop = asyncio.get_event_loop()
                loop.create_task(self.client.close())
                self.is_running = False
                logger.info("Бот остановлен")
        except Exception as e:
            logger.error(f"Ошибка при остановке бота: {e}")
            self.is_running = False

    def get_status(self) -> bool:
        """Возвращает статус бота."""
        return self.is_running and self.client is not None and self.client.is_running()
