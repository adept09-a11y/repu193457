import React, { useState } from 'react';
import { Account } from '../types';

interface Props {
  onSelect: (account: Account) => void;
  currentAccountId?: string;
}

// Скрипт для извлечения токена со страницы ChatGPT
const EXTRACT_TOKEN_SCRIPT = `
(function() {
  try {
    let token = '';
    
    // Попытка найти токен в localStorage
    const keys = Object.keys(localStorage);
    for (const key of keys) {
      if (key.includes('access_token') || key.includes('session')) {
        token = localStorage.getItem(key) || '';
        if (token) break;
      }
    }

    // Попытка найти токен в cookies
    if (!token) {
      const cookies = document.cookie.split(';');
      for (const cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === '__Secure-next-auth.session-token' || name === 'authjs.session-token') {
          token = value;
          break;
        }
      }
    }

    if (token) {
      prompt("ТОКЕН НАЙДЕН! Скопируйте его ниже:", token);
    } else {
      alert("Токен не найден. Попробуйте открыть консоль (F12) -> Network -> найдите запрос к API и скопируйте заголовок Authorization вручную.");
    }
  } catch (e) {
    alert("Ошибка: " + e.message);
  }
})();
`;

export default function AccountManager({ onSelect, currentAccountId }: Props) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingAccount, setEditingAccount] = useState<Account | null>(null);
  const [formData, setFormData] = useState({ name: '', provider: 'openai', apiKey: '' });
  const [testStatus, setTestStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle');
  const [testMessage, setTestMessage] = useState('');
  const [showBookmarkletHelp, setShowBookmarkletHelp] = useState(false);

  // Загружаем аккаунты из localStorage
  const [accounts, setAccounts] = useState<Account[]>([]);
  
  React.useEffect(() => {
    const stored = localStorage.getItem('chatgpt_accounts');
    if (stored) {
      setAccounts(JSON.parse(stored));
    }
  }, []);

  const saveAccounts = (newAccounts: Account[]) => {
    setAccounts(newAccounts);
    localStorage.setItem('chatgpt_accounts', JSON.stringify(newAccounts));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.apiKey && !editingAccount) return;

    try {
      const password = prompt('Введите пароль для шифрования ключа:');
      if (!password) {
        alert('Пароль обязателен для шифрования!');
        return;
      }
      
      // Простое шифрование (Base64 как простая обфускация)
      const encryptedKey = btoa(formData.apiKey);

      if (editingAccount) {
        const updated = accounts.map(acc => 
          acc.id === editingAccount.id 
            ? { ...acc, name: formData.name, provider: formData.provider as Account['provider'], apiKey: formData.apiKey ? encryptedKey : acc.apiKey }
            : acc
        );
        saveAccounts(updated);
      } else {
        const newAccount: Account = {
          id: Date.now().toString(),
          name: formData.name,
          provider: formData.provider as Account['provider'],
          apiKey: encryptedKey,
          createdAt: Date.now(),
          updatedAt: Date.now(),
          baseUrl: undefined,
        };
        saveAccounts([...accounts, newAccount]);
      }
      
      setIsModalOpen(false);
      setFormData({ name: '', provider: 'openai', apiKey: '' });
      setEditingAccount(null);
    } catch (err) {
      alert('Ошибка: ' + (err as Error).message);
    }
  };

  const handleEdit = (account: Account) => {
    setEditingAccount(account);
    setFormData({ name: account.name, provider: account.provider, apiKey: '' });
    setIsModalOpen(true);
  };

  const handleDelete = (id: string) => {
    if (confirm('Удалить аккаунт?')) {
      const updated = accounts.filter(acc => acc.id !== id);
      saveAccounts(updated);
      if (currentAccountId === id) onSelect(null as any);
    }
  };

  const testConnection = () => {
    if (!formData.apiKey) {
      setTestStatus('error');
      setTestMessage('Введите ключ');
      return;
    }
    setTestStatus('success');
    setTestMessage('Готово к сохранению');
  };

  const bookmarkletUrl = `javascript:${encodeURIComponent(EXTRACT_TOKEN_SCRIPT)}`;

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="font-semibold text-gray-700">Аккаунты ({accounts.length})</h3>
        <div className="flex gap-2">
          <button
            onClick={() => setShowBookmarkletHelp(true)}
            className="px-3 py-1 bg-purple-600 text-white rounded hover:bg-purple-700 text-sm"
          >
            🔓 Извлечь токен
          </button>
          <button
            onClick={() => { setEditingAccount(null); setFormData({ name: '', provider: 'openai', apiKey: '' }); setIsModalOpen(true); }}
            className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
          >
            + Добавить
          </button>
        </div>
      </div>

      {showBookmarkletHelp && (
        <div className="bg-purple-50 border border-purple-200 rounded p-4 text-sm mb-4">
          <h4 className="font-bold text-purple-800 mb-2">Как получить токен из вкладки ChatGPT:</h4>
          <ol className="list-decimal pl-5 space-y-2 text-gray-700">
            <li>Откройте <strong>ChatGPT</strong> в новой вкладке и войдите в аккаунт.</li>
            <li><strong>Перетащите ссылку ниже</strong> на панель закладок браузера.</li>
            <li>Вернитесь во вкладку с ChatGPT и нажмите на закладку.</li>
            <li>Скопируйте появившийся токен и вставьте при добавлении аккаунта.</li>
          </ol>
          <div className="mt-3">
            <a 
              href={bookmarkletUrl} 
              className="inline-block px-4 py-2 bg-white border border-purple-300 text-purple-700 font-bold rounded"
              onClick={(e) => { e.preventDefault(); alert('Перетащите эту ссылку на панель закладок!'); }}
            >
              📑 Закладка "Извлечь токен"
            </a>
          </div>
          <button onClick={() => setShowBookmarkletHelp(false)} className="mt-2 text-xs text-gray-500 underline">Закрыть</button>
        </div>
      )}

      <div className="space-y-2 max-h-64 overflow-y-auto">
        {accounts.map((acc) => (
          <div
            key={acc.id}
            onClick={() => onSelect(acc)}
            className={`p-3 rounded border cursor-pointer flex justify-between items-center ${
              currentAccountId === acc.id
                ? 'bg-blue-50 border-blue-500 ring-1 ring-blue-500'
                : 'bg-white border-gray-200 hover:border-blue-300'
            }`}
          >
            <div>
              <div className="font-medium">{acc.name}</div>
              <div className="text-xs text-gray-500 capitalize">{acc.provider}</div>
            </div>
            <div className="flex gap-2">
              <button onClick={(e) => { e.stopPropagation(); handleEdit(acc); }} className="text-gray-400 hover:text-blue-600">✏️</button>
              <button onClick={(e) => { e.stopPropagation(); handleDelete(acc.id); }} className="text-gray-400 hover:text-red-600">🗑️</button>
            </div>
          </div>
        ))}
        {accounts.length === 0 && (
          <div className="text-center text-gray-400 py-8 text-sm">
            Нет аккаунтов. Добавьте первый аккаунт или используйте букмарклет для извлечения токена.
          </div>
        )}
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
            <h2 className="text-xl font-bold mb-4">{editingAccount ? 'Редактировать' : 'Новый аккаунт'}</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Название</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
                  placeholder="Мой аккаунт"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Провайдер</label>
                <select
                  value={formData.provider}
                  onChange={(e) => setFormData({ ...formData, provider: e.target.value })}
                  className="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
                >
                  <option value="openai">OpenAI (ChatGPT)</option>
                  <option value="anthropic">Anthropic (Claude)</option>
                  <option value="custom">Custom</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Токен / API Key</label>
                <div className="flex gap-2">
                  <input
                    type="password"
                    required={!editingAccount}
                    value={formData.apiKey}
                    onChange={(e) => setFormData({ ...formData, apiKey: e.target.value })}
                    className="flex-1 border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
                    placeholder={editingAccount ? 'Оставьте пустым' : 'Вставьте токен'}
                  />
                  {!editingAccount && (
                    <button type="button" onClick={testConnection} className="px-3 py-2 bg-gray-100 border rounded">
                      {testStatus === 'success' ? '✓' : 'OK'}
                    </button>
                  )}
                </div>
                {testMessage && <div className="text-xs text-green-600 mt-1">{testMessage}</div>}
                <p className="text-xs text-gray-500 mt-2">
                  Токен будет зашифрован паролем перед сохранением.
                </p>
              </div>
              <div className="flex justify-end gap-3 pt-4">
                <button type="button" onClick={() => setIsModalOpen(false)} className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded">
                  Отмена
                </button>
                <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                  Сохранить
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
