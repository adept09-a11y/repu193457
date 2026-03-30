"""
Config Manager - Handles configuration loading, saving, and logging
"""
import json
import os
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CONFIG_FILE = "config.json"
LOG_FILE = "log.txt"

class ConfigManager:
    def __init__(self):
        self.config = self.load_config()
        self.setup_logging()
    
    def load_config(self):
        """Load configuration from JSON file"""
        default_config = {
            "tracked_users": [],
            "tracked_guilds": [],
            "telegram_chat_id": "",
            "discord_owner_id": "",
            "filter_mentions_only": False,
            "filter_keywords": [],
            "track_voice_events": True
        }
        
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config: {e}. Using defaults.")
                return default_config
        return default_config
    
    def save_config(self):
        """Save configuration to JSON file"""
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error saving config: {e}")
            return False
    
    def setup_logging(self):
        """Setup logging to file and console"""
        self.logger = logging.getLogger('DiscordToTelegram')
        self.logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # File handler
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def get_env_value(self, key, default=None):
        """Get value from environment variables"""
        return os.getenv(key, default)
    
    def add_tracked_user(self, user_id):
        """Add a tracked Discord user ID"""
        if user_id and user_id not in self.config["tracked_users"]:
            self.config["tracked_users"].append(str(user_id))
            return self.save_config()
        return False
    
    def remove_tracked_user(self, user_id):
        """Remove a tracked Discord user ID"""
        if str(user_id) in self.config["tracked_users"]:
            self.config["tracked_users"].remove(str(user_id))
            return self.save_config()
        return False
    
    def add_tracked_guild(self, guild_id):
        """Add a tracked Discord guild ID"""
        if guild_id and guild_id not in self.config["tracked_guilds"]:
            self.config["tracked_guilds"].append(str(guild_id))
            return self.save_config()
        return False
    
    def remove_tracked_guild(self, guild_id):
        """Remove a tracked Discord guild ID"""
        if str(guild_id) in self.config["tracked_guilds"]:
            self.config["tracked_guilds"].remove(str(guild_id))
            return self.save_config()
        return False
    
    def set_telegram_chat_id(self, chat_id):
        """Set Telegram chat ID for notifications"""
        self.config["telegram_chat_id"] = str(chat_id)
        return self.save_config()
    
    def set_discord_owner_id(self, owner_id):
        """Set Discord owner ID for mention filtering"""
        self.config["discord_owner_id"] = str(owner_id)
        return self.save_config()
    
    def set_filter_mentions_only(self, enabled):
        """Enable/disable mention-only filter"""
        self.config["filter_mentions_only"] = enabled
        return self.save_config()
    
    def set_track_voice_events(self, enabled):
        """Enable/disable voice event tracking"""
        self.config["track_voice_events"] = enabled
        return self.save_config()
    
    def add_keyword(self, keyword):
        """Add a keyword filter"""
        if keyword and keyword not in self.config["filter_keywords"]:
            self.config["filter_keywords"].append(keyword)
            return self.save_config()
        return False
    
    def remove_keyword(self, keyword):
        """Remove a keyword filter"""
        if keyword in self.config["filter_keywords"]:
            self.config["filter_keywords"].remove(keyword)
            return self.save_config()
        return False
    
    def get_log_content(self, lines=100):
        """Get last N lines from log file"""
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                return ''.join(all_lines[-lines:])
        except IOError:
            return "Log file not found or cannot be read."


# Global config manager instance
config_manager = ConfigManager()
