"""
Telegram Client - Handles sending notifications to Telegram
"""
import asyncio
from telegram import Bot
from telegram.error import TelegramError
from config_manager import config_manager

class TelegramClient:
    def __init__(self):
        self.bot = None
        self.token = None
        self.chat_id = None
        self.initialized = False
    
    def initialize(self):
        """Initialize Telegram bot with token from .env"""
        try:
            self.token = config_manager.get_env_value('TELEGRAM_BOT_TOKEN')
            if not self.token:
                config_manager.logger.error("Telegram bot token not found in .env")
                return False
            
            self.bot = Bot(token=self.token)
            self.chat_id = config_manager.config.get('telegram_chat_id')
            
            if not self.chat_id:
                config_manager.logger.error("Telegram chat ID not configured")
                return False
            
            self.initialized = True
            config_manager.logger.info("Telegram client initialized successfully")
            return True
        except Exception as e:
            config_manager.logger.error(f"Failed to initialize Telegram client: {e}")
            return False
    
    async def send_message(self, message, parse_mode='HTML'):
        """Send a message to the configured Telegram chat"""
        if not self.initialized:
            if not self.initialize():
                return False
        
        # Update chat_id from config (in case it changed)
        self.chat_id = config_manager.config.get('telegram_chat_id')
        
        if not self.chat_id:
            config_manager.logger.error("Telegram chat ID not set")
            return False
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode,
                disable_web_page_preview=False
            )
            config_manager.logger.info(f"Message sent to Telegram: {message[:50]}...")
            return True
        except TelegramError as e:
            config_manager.logger.error(f"Telegram error: {e}")
            return False
        except Exception as e:
            config_manager.logger.error(f"Unexpected error sending Telegram message: {e}")
            return False
    
    async def send_voice_notification(self, user_name, channel_name, guild_name, event_type):
        """Send a voice channel event notification"""
        emoji = "🎤" if event_type == "join" else "🔇"
        action = "Подключился к голосовому каналу" if event_type == "join" else "Покинул голосовой канал"
        
        message = (
            f"{emoji} <b>{action}</b>\n"
            f"👤 <b>Пользователь:</b> {user_name}\n"
            f"🔊 <b>Канал:</b> {channel_name}\n"
            f"🏠 <b>Сервер:</b> {guild_name}"
        )
        
        return await self.send_message(message)
    
    async def send_message_notification(self, timestamp, guild_name, channel_name, 
                                       author_name, author_id, content, message_url, attachments):
        """Send a message event notification"""
        # Escape special HTML characters in content
        safe_content = self._escape_html(content) if content else "<i>Нет текста</i>"
        safe_author = self._escape_html(author_name)
        safe_guild = self._escape_html(guild_name)
        safe_channel = self._escape_html(channel_name)
        
        message = (
            f"💬 <b>Новое сообщение</b>\n"
            f"⏰ <b>Время:</b> {timestamp}\n"
            f"🏠 <b>Сервер:</b> {safe_guild}\n"
            f"📝 <b>Канал:</b> {safe_channel}\n"
            f"👤 <b>Автор:</b> {safe_author} (<code>{author_id}</code>)\n"
            f"📄 <b>Текст:</b> {safe_content}"
        )
        
        if message_url:
            message += f"\n🔗 <a href='{message_url}'>Перейти к сообщению</a>"
        
        if attachments:
            attach_list = "\n".join([f"📎 {att}" for att in attachments[:5]])  # Limit to 5
            if len(attachments) > 5:
                attach_list += f"\n... и ещё {len(attachments) - 5} вложений"
            message += f"\n\n<b>Вложения:</b>\n{attach_list}"
        
        return await self.send_message(message)
    
    def _escape_html(self, text):
        """Escape HTML special characters"""
        if not text:
            return ""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;'))
    
    async def test_connection(self):
        """Test Telegram connection"""
        try:
            await self.bot.get_me()
            return True
        except Exception as e:
            config_manager.logger.error(f"Telegram connection test failed: {e}")
            return False


# Global telegram client instance
telegram_client = TelegramClient()
