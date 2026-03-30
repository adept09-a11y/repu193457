"""
main.py - Главное приложение с GUI

Точка входа приложения. Создает GUI интерфейс на Tkinter,
управляет запуском и остановкой бота.
"""

import asyncio
import logging
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from pathlib import Path

from config_manager import ConfigManager
from telegram_client import TelegramClient
from bot_worker import BotWorker


# Настройка логирования
def setup_logging():
    """Настройка системы логирования."""
    log_file = Path("log.txt")
    
    # Создание форматтера
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Обработчик файла
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Настройка корневого логгера
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return log_file


class LogViewer(tk.Toplevel):
    """Окно просмотра логов."""
    
    def __init__(self, parent, log_file: Path):
        super().__init__(parent)
        self.title("Просмотр логов")
        self.geometry("700x500")
        self.log_file = log_file
        
        self._create_widgets()
        self.load_logs()
    
    def _create_widgets(self):
        """Создание виджетов окна."""
        # Кнопки
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Обновить", command=self.load_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Очистить логи", command=self.clear_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Закрыть", command=self.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Текстовое поле для логов
        self.log_text = scrolledtext.ScrolledText(self, wrap=tk.WORD, font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Настройка тегов для цветов
        self.log_text.tag_configure("ERROR", foreground="red")
        self.log_text.tag_configure("WARNING", foreground="orange")
        self.log_text.tag_configure("INFO", foreground="green")
    
    def load_logs(self):
        """Загрузка логов из файла."""
        self.log_text.delete(1.0, tk.END)
        
        if not self.log_file.exists():
            self.log_text.insert(tk.END, "Файл логов не найден\n")
            return
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if "ERROR" in line:
                        self.log_text.insert(tk.END, line, "ERROR")
                    elif "WARNING" in line:
                        self.log_text.insert(tk.END, line, "WARNING")
                    elif "INFO" in line:
                        self.log_text.insert(tk.END, line, "INFO")
                    else:
                        self.log_text.insert(tk.END, line)
            
            # Прокрутка вниз
            self.log_text.see(tk.END)
            
        except Exception as e:
            self.log_text.insert(tk.END, f"Ошибка чтения логов: {e}\n")
    
    def clear_logs(self):
        """Очистка файла логов."""
        if messagebox.askyesno("Подтверждение", "Очистить файл логов?"):
            try:
                with open(self.log_file, 'w', encoding='utf-8') as f:
                    f.write("")
                self.load_logs()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось очистить логи: {e}")


class MainWindow:
    """Главное окно приложения."""
    
    def __init__(self):
        """Инициализация главного окна."""
        self.root = tk.Tk()
        self.root.title("Discord to Telegram Notifier")
        self.root.geometry("600x700")
        self.root.resizable(True, True)
        
        # Настройка логирования
        self.log_file = setup_logging()
        self.logger = logging.getLogger(__name__)
        self.logger.info("Приложение запущено")
        
        # Инициализация менеджеров
        self.config_manager = ConfigManager()
        self.telegram_client = TelegramClient(
            self.config_manager.telegram_token,
            self.config_manager.get_telegram_chat_id()
        )
        self.bot_worker = BotWorker(self.config_manager, self.telegram_client)
        
        # Настройка callback для статуса
        self.bot_worker.on_status_change = self.update_status
        
        # Переменные для потока бота
        self.bot_thread = None
        self.bot_loop = None
        self.stop_event = threading.Event()
        
        # Создание интерфейса
        self._create_widgets()
        self._load_config_to_ui()
        
        # Закрытие окна
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _create_widgets(self):
        """Создание виджетов интерфейса."""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # === Секция Telegram ===
        ttk.Label(main_frame, text="=== Telegram настройки ===", 
                 font=('Arial', 11, 'bold')).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        ttk.Label(main_frame, text="Chat ID:").grid(row=row, column=0, sticky=tk.W, pady=3)
        self.chat_id_var = tk.StringVar()
        self.chat_id_entry = ttk.Entry(main_frame, textvariable=self.chat_id_var, width=40)
        self.chat_id_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=3)
        row += 1
        
        # === Секция отслеживаемых пользователей ===
        ttk.Label(main_frame, text="=== Отслеживаемые пользователи ===", 
                 font=('Arial', 11, 'bold')).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        # Список пользователей
        user_list_frame = ttk.LabelFrame(main_frame, text="Пользователи (Discord ID)")
        user_list_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=3)
        user_list_frame.columnconfigure(0, weight=1)
        
        self.user_listbox = tk.Listbox(user_list_frame, height=5, font=('Consolas', 9))
        self.user_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Кнопки управления пользователями
        user_btn_frame = ttk.Frame(user_list_frame)
        user_btn_frame.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        ttk.Button(user_btn_frame, text="Добавить", command=self.add_user).pack(side=tk.LEFT, padx=2)
        ttk.Button(user_btn_frame, text="Удалить", command=self.remove_user).pack(side=tk.LEFT, padx=2)
        ttk.Button(user_btn_frame, text="Очистить", command=self.clear_users).pack(side=tk.LEFT, padx=2)
        
        row += 1
        
        # === Секция отслеживаемых серверов ===
        ttk.Label(main_frame, text="=== Отслеживаемые сервера ===", 
                 font=('Arial', 11, 'bold')).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        # Список серверов
        guild_list_frame = ttk.LabelFrame(main_frame, text="Сервера (Guild ID)")
        guild_list_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=3)
        guild_list_frame.columnconfigure(0, weight=1)
        
        self.guild_listbox = tk.Listbox(guild_list_frame, height=5, font=('Consolas', 9))
        self.guild_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Кнопки управления серверами
        guild_btn_frame = ttk.Frame(guild_list_frame)
        guild_btn_frame.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        ttk.Button(guild_btn_frame, text="Добавить", command=self.add_guild).pack(side=tk.LEFT, padx=2)
        ttk.Button(guild_btn_frame, text="Удалить", command=self.remove_guild).pack(side=tk.LEFT, padx=2)
        ttk.Button(guild_btn_frame, text="Очистить", command=self.clear_guilds).pack(side=tk.LEFT, padx=2)
        
        row += 1
        
        # === Секция фильтров ===
        ttk.Label(main_frame, text="=== Фильтры сообщений ===", 
                 font=('Arial', 11, 'bold')).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        self.filter_enabled_var = tk.BooleanVar(value=False)
        self.filter_check = ttk.Checkbutton(
            main_frame, 
            text="Включить фильтр (только упоминания владельца или ключевые слова)",
            variable=self.filter_enabled_var
        )
        self.filter_check.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=3)
        row += 1
        
        # Ключевые слова
        kw_frame = ttk.LabelFrame(main_frame, text="Ключевые слова")
        kw_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=3)
        kw_frame.columnconfigure(0, weight=1)
        
        self.kw_listbox = tk.Listbox(kw_frame, height=3, font=('Consolas', 9))
        self.kw_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        kw_btn_frame = ttk.Frame(kw_frame)
        kw_btn_frame.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        ttk.Button(kw_btn_frame, text="Добавить", command=self.add_keyword).pack(side=tk.LEFT, padx=2)
        ttk.Button(kw_btn_frame, text="Удалить", command=self.remove_keyword).pack(side=tk.LEFT, padx=2)
        
        row += 1
        
        # === Секция управления ботом ===
        ttk.Label(main_frame, text="=== Управление ботом ===", 
                 font=('Arial', 11, 'bold')).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        # Статус
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        ttk.Label(status_frame, text="Статус:").pack(side=tk.LEFT, padx=5)
        self.status_label = ttk.Label(status_frame, text="Stopped", font=('Arial', 10, 'bold'))
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        row += 1
        
        # Кнопки управления
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        self.start_btn = ttk.Button(control_frame, text="▶ Start Bot", command=self.start_bot)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(control_frame, text="⏹ Stop Bot", command=self.stop_bot, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="💾 Сохранить конфиг", command=self.save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="📋 Просмотр логов", command=self.show_logs).pack(side=tk.LEFT, padx=5)
        
        row += 1
        
        # Инфо панель
        info_frame = ttk.LabelFrame(main_frame, text="Информация")
        info_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        info_text = (
            "• Discord токен берется из .env файла\n"
            "• Для получения Discord ID включите режим разработчика в Discord\n"
            "• ПКМ по пользователю/серверу -> Копировать ID\n"
            "• Userbot может нарушать ToS Discord, используйте на свой риск"
        )
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W, padx=10, pady=10)
    
    def _load_config_to_ui(self):
        """Загрузка конфигурации в элементы UI."""
        # Chat ID
        self.chat_id_var.set(self.config_manager.get_telegram_chat_id())
        
        # Пользователи
        for user_id in self.config_manager.get_tracked_users():
            self.user_listbox.insert(tk.END, user_id)
        
        # Сервера
        for guild_id in self.config_manager.get_tracked_guilds():
            self.guild_listbox.insert(tk.END, guild_id)
        
        # Фильтр
        self.filter_enabled_var.set(self.config_manager.is_filter_enabled())
        
        # Ключевые слова
        for keyword in self.config_manager.get_keywords():
            self.kw_listbox.insert(tk.END, keyword)
    
    def add_user(self):
        """Добавление пользователя через диалог."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить пользователя")
        dialog.geometry("300x100")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Discord User ID:").pack(pady=5)
        entry = ttk.Entry(dialog, width=30)
        entry.pack(pady=5)
        entry.focus()
        
        def on_add():
            user_id = entry.get().strip()
            if user_id and user_id.isdigit():
                if self.config_manager.add_tracked_user(user_id):
                    self.user_listbox.insert(tk.END, user_id)
                    dialog.destroy()
                else:
                    messagebox.showwarning("Предупреждение", "Пользователь уже в списке")
            else:
                messagebox.showerror("Ошибка", "Введите корректный Discord ID")
        
        ttk.Button(dialog, text="Добавить", command=on_add).pack(pady=5)
        
        # Enter для добавления
        entry.bind('<Return>', lambda e: on_add())
    
    def remove_user(self):
        """Удаление выбранного пользователя."""
        selection = self.user_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для удаления")
            return
        
        user_id = self.user_listbox.get(selection[0])
        if self.config_manager.remove_tracked_user(user_id):
            self.user_listbox.delete(selection)
    
    def clear_users(self):
        """Очистка списка пользователей."""
        if messagebox.askyesno("Подтверждение", "Удалить всех пользователей из списка?"):
            self.config_manager.config["tracked_users"] = []
            self.user_listbox.delete(0, tk.END)
    
    def add_guild(self):
        """Добавление сервера через диалог."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить сервер")
        dialog.geometry("300x100")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Discord Guild ID:").pack(pady=5)
        entry = ttk.Entry(dialog, width=30)
        entry.pack(pady=5)
        entry.focus()
        
        def on_add():
            guild_id = entry.get().strip()
            if guild_id and guild_id.isdigit():
                if self.config_manager.add_tracked_guild(guild_id):
                    self.guild_listbox.insert(tk.END, guild_id)
                    dialog.destroy()
                else:
                    messagebox.showwarning("Предупреждение", "Сервер уже в списке")
            else:
                messagebox.showerror("Ошибка", "Введите корректный Guild ID")
        
        ttk.Button(dialog, text="Добавить", command=on_add).pack(pady=5)
        entry.bind('<Return>', lambda e: on_add())
    
    def remove_guild(self):
        """Удаление выбранного сервера."""
        selection = self.guild_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите сервер для удаления")
            return
        
        guild_id = self.guild_listbox.get(selection[0])
        if self.config_manager.remove_tracked_guild(guild_id):
            self.guild_listbox.delete(selection)
    
    def clear_guilds(self):
        """Очистка списка серверов."""
        if messagebox.askyesno("Подтверждение", "Удалить все сервера из списка?"):
            self.config_manager.config["tracked_guilds"] = []
            self.guild_listbox.delete(0, tk.END)
    
    def add_keyword(self):
        """Добавление ключевого слова."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить ключевое слово")
        dialog.geometry("300x100")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Ключевое слово:").pack(pady=5)
        entry = ttk.Entry(dialog, width=30)
        entry.pack(pady=5)
        entry.focus()
        
        def on_add():
            keyword = entry.get().strip()
            if keyword:
                if self.config_manager.add_keyword(keyword):
                    self.kw_listbox.insert(tk.END, keyword.lower())
                    dialog.destroy()
                else:
                    messagebox.showwarning("Предупреждение", "Слово уже в списке")
            else:
                messagebox.showerror("Ошибка", "Введите ключевое слово")
        
        ttk.Button(dialog, text="Добавить", command=on_add).pack(pady=5)
        entry.bind('<Return>', lambda e: on_add())
    
    def remove_keyword(self):
        """Удаление ключевого слова."""
        selection = self.kw_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите слово для удаления")
            return
        
        keyword = self.kw_listbox.get(selection[0])
        if self.config_manager.remove_keyword(keyword):
            self.kw_listbox.delete(selection)
    
    def save_config(self):
        """Сохранение конфигурации."""
        # Обновление конфигурации из UI
        self.config_manager.set_telegram_chat_id(self.chat_id_var.get().strip())
        self.config_manager.set_filter_enabled(self.filter_enabled_var.get())
        
        # Сохранение
        if self.config_manager.save_config():
            self.logger.info("Конфигурация сохранена")
            messagebox.showinfo("Успех", "Конфигурация успешно сохранена!")
            
            # Обновление Telegram chat_id
            self.telegram_client.set_chat_id(self.config_manager.get_telegram_chat_id())
        else:
            self.logger.error("Ошибка сохранения конфигурации")
            messagebox.showerror("Ошибка", "Не удалось сохранить конфигурацию")
    
    def start_bot(self):
        """Запуск бота в отдельном потоке."""
        if self.bot_worker.is_running:
            messagebox.showwarning("Предупреждение", "Бот уже запущен")
            return
        
        # Проверка токена
        if not self.config_manager.discord_token:
            messagebox.showerror("Ошибка", "Discord токен не найден в .env файле")
            return
        
        # Сохранение конфигурации перед запуском
        self.save_config()
        
        # Проверка наличия отслеживаемых пользователей
        if not self.config_manager.get_tracked_users():
            if not messagebox.askyesno("Предупреждение", 
                "Список отслеживаемых пользователей пуст.\nЗапустить без пользователей?"):
                return
        
        # Запуск в потоке
        self.bot_thread = threading.Thread(target=self._run_bot, daemon=True)
        self.bot_thread.start()
        
        self.logger.info("Бот запущен в отдельном потоке")
    
    def _run_bot(self):
        """Запуск цикла событий бота в потоке."""
        self.bot_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.bot_loop)
        
        try:
            self.bot_loop.run_until_complete(self.bot_worker.start())
        except Exception as e:
            self.logger.error(f"Ошибка в цикле бота: {e}")
            self.root.after(0, lambda: self.update_status(f"Error: {e}"))
        finally:
            self.bot_loop.close()
    
    def stop_bot(self):
        """Остановка бота."""
        if not self.bot_worker.is_running:
            return
        
        self.logger.info("Остановка бота...")
        
        # Остановка в цикле событий бота
        if self.bot_loop and self.bot_loop.is_running():
            self.bot_loop.call_soon_threadsafe(
                lambda: asyncio.create_task(self.bot_worker.stop())
            )
        
        self.stop_btn.config(state=tk.DISABLED)
        self.start_btn.config(state=tk.NORMAL)
    
    def update_status(self, status: str):
        """Обновление статуса бота (вызывается из другого потока)."""
        def update():
            self.status_label.config(text=status)
            if "Connected" in status or "Running" in status:
                self.stop_btn.config(state=tk.NORMAL)
                self.start_btn.config(state=tk.DISABLED)
            elif "Stopped" in status or "Error" in status:
                self.stop_btn.config(state=tk.DISABLED)
                self.start_btn.config(state=tk.NORMAL)
        
        self.root.after(0, update)
    
    def show_logs(self):
        """Показ окна просмотра логов."""
        LogViewer(self.root, self.log_file)
    
    def _on_closing(self):
        """Обработчик закрытия окна."""
        if self.bot_worker.is_running:
            if messagebox.askyesno("Подтверждение", 
                "Бот работает. Остановить и выйти?"):
                self.stop_bot()
                self.root.after(1000, self.root.destroy)
            else:
                return
        
        self.logger.info("Приложение закрыто")
        self.root.destroy()
    
    def run(self):
        """Запуск главного цикла приложения."""
        self.root.mainloop()


if __name__ == "__main__":
    app = MainWindow()
    app.run()
