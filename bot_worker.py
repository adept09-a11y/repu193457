"""
Bot Worker - Discord userbot logic for monitoring messages and voice events
Uses discord.py-self for userbot functionality
"""
import asyncio
from datetime import datetime
import discord
from config_manager import config_manager
from telegram_client import telegram_client

class DiscordUserbot:
    def __init__(self):
        self.client = None
        self.running = False
        self.task = None
        
        # GuildSubscriptionOptions for discord.py-self (instead of Intents)
        # This controls what events and data the client subscribes to
        self.options = discord.GuildSubscriptionOptions.default()
    
    async def start(self, token):
        """Start the Discord userbot"""
        try:
            if not token:
                config_manager.logger.error("Discord token not provided")
                return False
            
            # Create client with GuildSubscriptionOptions (discord.py-self API)
            self.client = discord.Client(options=self.options)
            
            @self.client.event
            async def on_ready():
                config_manager.logger.info(f"Discord userbot logged in as {self.client.user}")
                self.running = True
            
            @self.client.event
            async def on_message(message):
                await self.handle_message(message)
            
            @self.client.event
            async def on_voice_state_update(member, before, after):
                await self.handle_voice_update(member, before, after)
            
            # Start the client in a separate task
            self.task = asyncio.create_task(self.client.start(token))
            
            # Wait a bit to ensure connection
            await asyncio.sleep(3)
            
            if self.running:
                config_manager.logger.info("Discord userbot started successfully")
                return True
            return False
            
        except Exception as e:
            config_manager.logger.error(f"Failed to start Discord userbot: {e}")
            return False
    
    async def stop(self):
        """Stop the Discord userbot"""
        try:
            self.running = False
            if self.client and self.client.is_ready():
                await self.client.close()
            if self.task:
                self.task.cancel()
                try:
                    await self.task
                except asyncio.CancelledError:
                    pass
            config_manager.logger.info("Discord userbot stopped")
            return True
        except Exception as e:
            config_manager.logger.error(f"Error stopping Discord userbot: {e}")
            return False
    
    async def handle_message(self, message):
        """Handle incoming message events"""
        try:
            # Ignore our own messages
            if message.author.id == self.client.user.id:
                return
            
            # Ignore bots (optional, can be configured)
            if message.author.bot:
                return
            
            # Check if user is tracked
            author_id = str(message.author.id)
            tracked_users = config_manager.config.get('tracked_users', [])
            
            if author_id not in tracked_users:
                return
            
            # Check if guild is tracked (if guild exists)
            guild_id = str(message.guild.id) if message.guild else None
            tracked_guilds = config_manager.config.get('tracked_guilds', [])
            
            if message.guild and guild_id not in tracked_guilds:
                return
            
            # Apply filters
            if not self.should_forward_message(message):
                return
            
            # Prepare notification data
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            guild_name = message.guild.name if message.guild else "Личные сообщения"
            channel_name = f"#{message.channel.name}" if hasattr(message.channel, 'name') else "Unknown"
            author_name = f"{message.author.name}#{message.author.discriminator}"
            content = message.content
            message_url = f"https://discord.com/channels/{guild_id}/{message.channel.id}/{message.id}" if message.guild else None
            
            # Get attachments
            attachments = [att.url for att in message.attachments] if message.attachments else []
            
            # Send to Telegram
            await telegram_client.send_message_notification(
                timestamp=timestamp,
                guild_name=guild_name,
                channel_name=channel_name,
                author_name=author_name,
                author_id=author_id,
                content=content,
                message_url=message_url,
                attachments=attachments
            )
            
        except Exception as e:
            config_manager.logger.error(f"Error handling message: {e}")
    
    async def handle_voice_update(self, member, before, after):
        """Handle voice state update events"""
        try:
            # Check if voice tracking is enabled
            if not config_manager.config.get('track_voice_events', True):
                return
            
            # Ignore our own updates
            if member.id == self.client.user.id:
                return
            
            # Check if member is tracked
            member_id = str(member.id)
            tracked_users = config_manager.config.get('tracked_users', [])
            
            if member_id not in tracked_users:
                return
            
            # Check if guild is tracked
            guild_id = str(member.guild.id) if member.guild else None
            tracked_guilds = config_manager.config.get('tracked_guilds', [])
            
            if member.guild and guild_id not in tracked_guilds:
                return
            
            # Determine event type
            event_type = None
            channel_name = "Unknown"
            guild_name = member.guild.name if member.guild else "Unknown"
            
            if before.channel is None and after.channel is not None:
                # User joined a voice channel
                event_type = "join"
                channel_name = after.channel.name
            elif before.channel is not None and after.channel is None:
                # User left a voice channel
                event_type = "leave"
                channel_name = before.channel.name
            elif before.channel != after.channel and before.channel and after.channel:
                # User switched channels - send leave then join
                # First: leave old channel
                await telegram_client.send_voice_notification(
                    user_name=f"{member.name}#{member.discriminator}",
                    channel_name=before.channel.name,
                    guild_name=guild_name,
                    event_type="leave"
                )
                # Then: join new channel
                await telegram_client.send_voice_notification(
                    user_name=f"{member.name}#{member.discriminator}",
                    channel_name=after.channel.name,
                    guild_name=guild_name,
                    event_type="join"
                )
                return
            
            if event_type:
                await telegram_client.send_voice_notification(
                    user_name=f"{member.name}#{member.discriminator}",
                    channel_name=channel_name,
                    guild_name=guild_name,
                    event_type=event_type
                )
            
        except Exception as e:
            config_manager.logger.error(f"Error handling voice update: {e}")
    
    def should_forward_message(self, message):
        """Check if message should be forwarded based on filters"""
        config = config_manager.config
        
        # If mention-only filter is enabled
        if config.get('filter_mentions_only', False):
            owner_id = config.get('discord_owner_id')
            if owner_id and message.mentions:
                # Check if owner is mentioned
                for mention in message.mentions:
                    if str(mention.id) == owner_id:
                        return True
            # Also check for role mentions or everyone mention
            if message.mention_everyone:
                return True
            return False
        
        # If keywords filter is set
        keywords = config.get('filter_keywords', [])
        if keywords and message.content:
            content_lower = message.content.lower()
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    return True
            # If keywords are set but not found, don't forward
            if keywords:
                return False
        
        # No filters or filters passed
        return True


# Global bot worker instance
bot_worker = DiscordUserbot()
