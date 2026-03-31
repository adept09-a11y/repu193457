"""
Main Application - GUI and application entry point
Discord to Telegram Notification App with Tkinter GUI (Dark Theme)
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import asyncio
import threading
from dotenv import load_dotenv
import os

from config_manager import config_manager
from bot_worker import DiscordUserbot
from telegram_client import telegram_client

# Load environment variables
load_dotenv()


class DiscordToTelegramApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Discord → Telegram Notifications")
        self.root.geometry("950x750")
        
        # Configure dark theme colors
        self.bg_color = "#2b2b2b"
        self.fg_color = "#ffffff"
        self.entry_bg = "#3c3f41"
        self.button_bg = "#4a4a4a"
        self.button_fg = "#ffffff"
        self.accent_color = "#5a9fd4"
        self.listbox_bg = "#3c3f41"
        
        # Apply dark theme to root
        self.root.configure(bg=self.bg_color)
        
        # Configure ttk styles for dark theme
        self.setup_dark_theme()
        
        # Bot instances
        self.discord_bot = None
        self.bot_running = False
        
        # Create UI components
        self.create_widgets()
        
        # Load current config into UI
        self.load_config_to_ui()
    
    def setup_dark_theme(self):
        """Setup dark theme for ttk widgets"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure common styles
        style.configure('.', background=self.bg_color, foreground=self.fg_color,
                       fieldbackground=self.entry_bg)
        style.configure('TLabel', background=self.bg_color, foreground=self.fg_color)
        style.configure('TButton', background=self.button_bg, foreground=self.button_fg,
                       borderwidth=1, focuscolor='none')
        style.map('TButton', background=[('active', self.accent_color)])
        style.configure('TEntry', fieldbackground=self.entry_bg, foreground=self.fg_color,
                       borderwidth=1)
        style.configure('TCheckbutton', background=self.bg_color, foreground=self.fg_color,
                       indicatorbackground=self.bg_color)
        style.map('TCheckbutton', background=[('active', self.bg_color)])
        style.configure('Treeview', background=self.listbox_bg, foreground=self.fg_color,
                       fieldbackground=self.listbox_bg)
        style.configure('Treeview.Heading', background=self.button_bg, foreground=self.fg_color)
        style.map('Treeview', background=[('selected', self.accent_color)])
    
    def create_widgets(self):
        """Create all UI widgets"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # === Environment Variables Section ===
        env_frame = ttk.LabelFrame(main_frame, text="🔐 Настройки .env (токены)", padding="10")
        env_frame.grid(row=row, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        env_frame.columnconfigure(1, weight=1)
        
        # Discord Token
        ttk.Label(env_frame, text="Discord Token:").grid(row=0, column=0, sticky="w", pady=5)
        self.discord_token_var = tk.StringVar()
        self.discord_token_entry = ttk.Entry(env_frame, textvariable=self.discord_token_var, show="*")
        self.discord_token_entry.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Telegram Bot Token
        ttk.Label(env_frame, text="Telegram Bot Token:").grid(row=1, column=0, sticky="w", pady=5)
        self.telegram_token_var = tk.StringVar()
        self.telegram_token_entry = ttk.Entry(env_frame, textvariable=self.telegram_token_var, show="*")
        self.telegram_token_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Save .env button
        ttk.Button(env_frame, text="💾 Сохранить .env", command=self.save_env).grid(row=2, column=1, sticky="e", pady=5)
        
        row += 1
        
        # === Telegram Settings Section ===
        tg_frame = ttk.LabelFrame(main_frame, text="📱 Telegram Настройки", padding="10")
        tg_frame.grid(row=row, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        tg_frame.columnconfigure(1, weight=1)
        
        # Chat ID
        ttk.Label(tg_frame, text="Telegram Chat ID:").grid(row=0, column=0, sticky="w", pady=5)
        self.chat_id_var = tk.StringVar()
        self.chat_id_entry = ttk.Entry(tg_frame, textvariable=self.chat_id_var)
        self.chat_id_entry.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Test connection button
        ttk.Button(tg_frame, text="🧪 Тест соединения", command=self.test_telegram).grid(row=0, column=2, sticky="w", padx=(10, 0), pady=5)
        
        row += 1
        
        # === Discord Settings Section ===
        disc_frame = ttk.LabelFrame(main_frame, text="🎮 Discord Настройки", padding="10")
        disc_frame.grid(row=row, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        disc_frame.columnconfigure(1, weight=1)
        
        # Owner ID
        ttk.Label(disc_frame, text="Discord Owner ID:").grid(row=0, column=0, sticky="w", pady=5)
        self.owner_id_var = tk.StringVar()
        self.owner_id_entry = ttk.Entry(disc_frame, textvariable=self.owner_id_var)
        self.owner_id_entry.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
        ttk.Label(disc_frame, text="(для фильтра упоминаний)", font=('TkDefaultFont', 8)).grid(row=0, column=2, sticky="w", padx=(5, 0), pady=5)
        
        row += 1
        
        # === Tracked Users Section ===
        users_frame = ttk.LabelFrame(main_frame, text="👥 Отслеживаемые пользователи", padding="10")
        users_frame.grid(row=row, column=0, sticky="nsew", pady=(0, 10), padx=(0, 5))
        users_frame.columnconfigure(0, weight=1)
        users_frame.rowconfigure(1, weight=1)
        
        # Add user controls
        add_user_frame = ttk.Frame(users_frame)
        add_user_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        add_user_frame.columnconfigure(0, weight=1)
        
        self.add_user_var = tk.StringVar()
        ttk.Entry(add_user_frame, textvariable=self.add_user_var, width=20).grid(row=0, column=0, sticky="ew")
        ttk.Button(add_user_frame, text="➕ Добавить", command=self.add_user).grid(row=0, column=1, sticky="w", padx=(5, 0))
        
        # Users listbox
        self.users_listbox = tk.Listbox(users_frame, bg=self.listbox_bg, fg=self.fg_color, 
                                        selectbackground=self.accent_color, height=6)
        self.users_listbox.grid(row=1, column=0, sticky="nsew")
        
        # Remove user button
        ttk.Button(users_frame, text="➖ Удалить выбранного", command=self.remove_user).grid(row=2, column=0, sticky="e", pady=(5, 0))
        
        row += 1
        
        # === Tracked Guilds Section ===
        guilds_frame = ttk.LabelFrame(main_frame, text="🏠 Отслеживаемые сервера", padding="10")
        guilds_frame.grid(row=row, column=1, sticky="nsew", pady=(0, 10), padx=(0, 5))
        guilds_frame.columnconfigure(0, weight=1)
        guilds_frame.rowconfigure(1, weight=1)
        
        # Add guild controls
        add_guild_frame = ttk.Frame(guilds_frame)
        add_guild_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        add_guild_frame.columnconfigure(0, weight=1)
        
        self.add_guild_var = tk.StringVar()
        ttk.Entry(add_guild_frame, textvariable=self.add_guild_var, width=20).grid(row=0, column=0, sticky="ew")
        ttk.Button(add_guild_frame, text="➕ Добавить", command=self.add_guild).grid(row=0, column=1, sticky="w", padx=(5, 0))
        
        # Guilds listbox
        self.guilds_listbox = tk.Listbox(guilds_frame, bg=self.listbox_bg, fg=self.fg_color,
                                         selectbackground=self.accent_color, height=6)
        self.guilds_listbox.grid(row=1, column=0, sticky="nsew")
        
        # Remove guild button
        ttk.Button(guilds_frame, text="➖ Удалить выбранный", command=self.remove_guild).grid(row=2, column=0, sticky="e", pady=(5, 0))
        
        row += 1
        
        # === Filters Section ===
        filters_frame = ttk.LabelFrame(main_frame, text="🔍 Фильтры", padding="10")
        filters_frame.grid(row=row, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        filters_frame.columnconfigure(1, weight=1)
        
        # Mention only checkbox
        self.mention_only_var = tk.BooleanVar()
        ttk.Checkbutton(filters_frame, text="Только упоминания владельца", 
                       variable=self.mention_only_var, command=self.toggle_mention_filter).grid(row=0, column=0, sticky="w", pady=5)
        
        # Voice events checkbox
        self.voice_events_var = tk.BooleanVar()
        ttk.Checkbutton(filters_frame, text="Отслеживать голосовые события",
                       variable=self.voice_events_var, command=self.toggle_voice_events).grid(row=0, column=1, sticky="w", pady=5)
        
        # Keywords
        ttk.Label(filters_frame, text="Ключевые слова:").grid(row=1, column=0, sticky="w", pady=5)
        self.keywords_var = tk.StringVar()
        keywords_entry = ttk.Entry(filters_frame, textvariable=self.keywords_var)
        keywords_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        ttk.Button(filters_frame, text="➕ Добавить слово", command=self.add_keyword).grid(row=1, column=2, sticky="w", padx=(5, 0), pady=5)
        
        # Keywords listbox
        self.keywords_listbox = tk.Listbox(filters_frame, bg=self.listbox_bg, fg=self.fg_color,
                                           selectbackground=self.accent_color, height=3)
        self.keywords_listbox.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(5, 0))
        
        ttk.Button(filters_frame, text="➖ Удалить слово", command=self.remove_keyword).grid(row=3, column=0, sticky="w", pady=(5, 0))
        
        row += 1
        
        # === Control Buttons Section ===
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=row, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        control_frame.columnconfigure((0, 1, 2, 3), weight=1)
        
        self.start_button = ttk.Button(control_frame, text="▶️ Start Bot", command=self.start_bot)
        self.start_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        self.stop_button = ttk.Button(control_frame, text="⏹️ Stop Bot", command=self.stop_bot, state='disabled')
        self.stop_button.grid(row=0, column=1, sticky="ew", padx=(0, 5))
        
        ttk.Button(control_frame, text="💾 Сохранить конфиг", command=self.save_config).grid(row=0, column=2, sticky="ew", padx=(0, 5))
        
        ttk.Button(control_frame, text="📋 Просмотр логов", command=self.show_logs).grid(row=0, column=3, sticky="ew")
        
        row += 1
        
        # === Status Section ===
        status_frame = ttk.LabelFrame(main_frame, text="📊 Статус", padding="10")
        status_frame.grid(row=row, column=0, columnspan=3, sticky="ew")
        
        self.status_label = ttk.Label(status_frame, text="❌ Бот остановлен", font=('TkDefaultFont', 10, 'bold'))
        self.status_label.pack(anchor='w')
        
        self.info_label = ttk.Label(status_frame, text="", font=('TkDefaultFont', 8))
        self.info_label.pack(anchor='w')
    
    def load_config_to_ui(self):
        """Load current configuration into UI fields"""
        # Load from .env
        self.discord_token_var.set(os.getenv('DISCORD_TOKEN', ''))
        self.telegram_token_var.set(os.getenv('TELEGRAM_BOT_TOKEN', ''))
        
        # Load from config.json
        config = config_manager.config
        self.chat_id_var.set(config.get('telegram_chat_id', ''))
        self.owner_id_var.set(config.get('discord_owner_id', ''))
        self.mention_only_var.set(config.get('filter_mentions_only', False))
        self.voice_events_var.set(config.get('track_voice_events', True))
        
        # Load lists
        self.users_listbox.delete(0, tk.END)
        for user in config.get('tracked_users', []):
            self.users_listbox.insert(tk.END, user)
        
        self.guilds_listbox.delete(0, tk.END)
        for guild in config.get('tracked_guilds', []):
            self.guilds_listbox.insert(tk.END, guild)
        
        self.keywords_listbox.delete(0, tk.END)
        for keyword in config.get('filter_keywords', []):
            self.keywords_listbox.insert(tk.END, keyword)
    
    def save_env(self):
        """Save environment variables to .env file"""
        try:
            discord_token = self.discord_token_var.get().strip()
            telegram_token = self.telegram_token_var.get().strip()
            
            if not discord_token or not telegram_token:
                messagebox.showwarning("Предупреждение", "Оба токена должны быть заполнены!")
                return
            
            config_manager.set_discord_token(discord_token)
            config_manager.set_telegram_token(telegram_token)
            
            # Reload environment
            load_dotenv(override=True)
            
            messagebox.showinfo("Успех", ".env файл сохранён успешно!")
            config_manager.logger.info(".env file saved")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить .env: {e}")
            config_manager.logger.error(f"Error saving .env: {e}")
    
    def test_telegram(self):
        """Test Telegram connection"""
        chat_id = self.chat_id_var.get().strip()
        if not chat_id:
            messagebox.showwarning("Предупреждение", "Сначала укажите Telegram Chat ID!")
            return
        
        def run_test():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(telegram_client.test_connection())
                if result:
                    self.root.after(0, lambda: messagebox.showinfo("Успех", "Соединение с Telegram установлено!"))
                else:
                    self.root.after(0, lambda: messagebox.showerror("Ошибка", "Не удалось подключиться к Telegram. Проверьте токен и Chat ID."))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Ошибка: {e}"))
            finally:
                loop.close()
        
        threading.Thread(target=run_test, daemon=True).start()
    
    def add_user(self):
        """Add tracked user"""
        user_id = self.add_user_var.get().strip()
        if user_id:
            if config_manager.add_tracked_user(user_id):
                self.users_listbox.insert(tk.END, user_id)
                self.add_user_var.set('')
                config_manager.logger.info(f"Added tracked user: {user_id}")
            else:
                messagebox.showwarning("Предупреждение", "Пользователь уже добавлен или ошибка сохранения")
        else:
            messagebox.showwarning("Предупреждение", "Введите Discord User ID")
    
    def remove_user(self):
        """Remove tracked user"""
        selection = self.users_listbox.curselection()
        if selection:
            user_id = self.users_listbox.get(selection[0])
            if config_manager.remove_tracked_user(user_id):
                self.users_listbox.delete(selection)
                config_manager.logger.info(f"Removed tracked user: {user_id}")
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить пользователя")
        else:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для удаления")
    
    def add_guild(self):
        """Add tracked guild"""
        guild_id = self.add_guild_var.get().strip()
        if guild_id:
            if config_manager.add_tracked_guild(guild_id):
                self.guilds_listbox.insert(tk.END, guild_id)
                self.add_guild_var.set('')
                config_manager.logger.info(f"Added tracked guild: {guild_id}")
            else:
                messagebox.showwarning("Предупреждение", "Сервер уже добавлен или ошибка сохранения")
        else:
            messagebox.showwarning("Предупреждение", "Введите Discord Guild ID")
    
    def remove_guild(self):
        """Remove tracked guild"""
        selection = self.guilds_listbox.curselection()
        if selection:
            guild_id = self.guilds_listbox.get(selection[0])
            if config_manager.remove_tracked_guild(guild_id):
                self.guilds_listbox.delete(selection)
                config_manager.logger.info(f"Removed tracked guild: {guild_id}")
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить сервер")
        else:
            messagebox.showwarning("Предупреждение", "Выберите сервер для удаления")
    
    def toggle_mention_filter(self):
        """Toggle mention filter"""
        enabled = self.mention_only_var.get()
        config_manager.set_mention_filter(enabled)
        config_manager.logger.info(f"Mention filter: {'enabled' if enabled else 'disabled'}")
    
    def toggle_voice_events(self):
        """Toggle voice events tracking"""
        enabled = self.voice_events_var.get()
        config_manager.set_track_voice_events(enabled)
        config_manager.logger.info(f"Voice events tracking: {'enabled' if enabled else 'disabled'}")
    
    def add_keyword(self):
        """Add keyword"""
        keyword = self.keywords_var.get().strip()
        if keyword:
            if config_manager.add_keyword(keyword):
                self.keywords_listbox.insert(tk.END, keyword)
                self.keywords_var.set('')
                config_manager.logger.info(f"Added keyword: {keyword}")
            else:
                messagebox.showwarning("Предупреждение", "Ключевое слово уже добавлено")
        else:
            messagebox.showwarning("Предупреждение", "Введите ключевое слово")
    
    def remove_keyword(self):
        """Remove keyword"""
        selection = self.keywords_listbox.curselection()
        if selection:
            keyword = self.keywords_listbox.get(selection[0])
            if config_manager.remove_keyword(keyword):
                self.keywords_listbox.delete(selection)
                config_manager.logger.info(f"Removed keyword: {keyword}")
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить ключевое слово")
        else:
            messagebox.showwarning("Предупреждение", "Выберите ключевое слово для удаления")
    
    def start_bot(self):
        """Start the Discord bot"""
        if self.bot_running:
            messagebox.showwarning("Предупреждение", "Бот уже запущен!")
            return
        
        # Validate required settings
        if not self.discord_token_var.get().strip():
            messagebox.showerror("Ошибка", "Укажите Discord Token в настройках .env!")
            return
        
        if not self.telegram_token_var.get().strip():
            messagebox.showerror("Ошибка", "Укажите Telegram Bot Token в настройках .env!")
            return
        
        if not self.chat_id_var.get().strip():
            messagebox.showerror("Ошибка", "Укажите Telegram Chat ID!")
            return
        
        # Save current settings
        config_manager.set_telegram_chat_id(self.chat_id_var.get().strip())
        config_manager.set_discord_owner_id(self.owner_id_var.get().strip())
        
        # Create bot instance
        self.discord_bot = DiscordUserbot(config_manager, telegram_client)
        
        # Start bot in separate thread
        def run_bot():
            try:
                self.discord_bot.start()
            except Exception as e:
                config_manager.logger.error(f"Bot error: {e}")
                self.root.after(0, lambda: messagebox.showerror("Ошибка бота", str(e)))
                self.root.after(0, self._on_bot_stop)
        
        thread = threading.Thread(target=run_bot, daemon=True)
        thread.start()
        
        # Update UI
        self.bot_running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.status_label.config(text="✅ Бот запущен", foreground="#4caf50")
        self.info_label.config(text=f"Мониторинг {len(self.users_listbox.get(0, tk.END))} пользователей на {len(self.guilds_listbox.get(0, tk.END))} серверах")
        config_manager.logger.info("Bot started via GUI")
    
    def stop_bot(self):
        """Stop the Discord bot"""
        if not self.bot_running:
            messagebox.showwarning("Предупреждение", "Бот не запущен!")
            return
        
        if self.discord_bot:
            self.discord_bot.stop()
        
        self._on_bot_stop()
    
    def _on_bot_stop(self):
        """Handle bot stop event"""
        self.bot_running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_label.config(text="❌ Бот остановлен", foreground="#f44336")
        self.info_label.config(text="")
        config_manager.logger.info("Bot stopped via GUI")
    
    def save_config(self):
        """Save current configuration"""
        try:
            # Save tokens to .env
            if self.discord_token_var.get().strip():
                config_manager.set_discord_token(self.discord_token_var.get().strip())
            if self.telegram_token_var.get().strip():
                config_manager.set_telegram_token(self.telegram_token_var.get().strip())
            
            # Save other settings
            config_manager.set_telegram_chat_id(self.chat_id_var.get().strip())
            config_manager.set_discord_owner_id(self.owner_id_var.get().strip())
            config_manager.set_mention_filter(self.mention_only_var.get())
            config_manager.set_track_voice_events(self.voice_events_var.get())
            
            # Clear and reload lists
            config_manager.config['tracked_users'] = list(self.users_listbox.get(0, tk.END))
            config_manager.config['tracked_guilds'] = list(self.guilds_listbox.get(0, tk.END))
            config_manager.config['filter_keywords'] = list(self.keywords_listbox.get(0, tk.END))
            config_manager.save_config()
            
            messagebox.showinfo("Успех", "Конфигурация сохранена!")
            config_manager.logger.info("Configuration saved")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить конфигурацию: {e}")
            config_manager.logger.error(f"Error saving config: {e}")
    
    def show_logs(self):
        """Show logs in a new window"""
        log_window = tk.Toplevel(self.root)
        log_window.title("📋 Логи приложения")
        log_window.geometry("700x500")
        log_window.configure(bg=self.bg_color)
        
        # Text widget for logs
        log_text = scrolledtext.ScrolledText(log_window, bg=self.listbox_bg, fg=self.fg_color, 
                                             insertbackground=self.fg_color, wrap=tk.WORD)
        log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Load logs from file
        try:
            with open('log.txt', 'r', encoding='utf-8') as f:
                logs = f.read()
            log_text.insert(tk.END, logs)
            log_text.see(tk.END)
        except FileNotFoundError:
            log_text.insert(tk.END, "Лог-файл ещё не создан.\n")
        except Exception as e:
            log_text.insert(tk.END, f"Ошибка чтения логов: {e}\n")
        
        # Refresh button
        def refresh_logs():
            log_text.delete(1.0, tk.END)
            try:
                with open('log.txt', 'r', encoding='utf-8') as f:
                    logs = f.read()
                log_text.insert(tk.END, logs)
                log_text.see(tk.END)
            except Exception as e:
                log_text.insert(tk.END, f"Ошибка чтения логов: {e}\n")
        
        ttk.Button(log_window, text="🔄 Обновить", command=refresh_logs).pack(pady=(0, 10))


def main():
    """Application entry point"""
    root = tk.Tk()
    app = DiscordToTelegramApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
