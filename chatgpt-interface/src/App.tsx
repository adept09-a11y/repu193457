import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { ChatPanel } from './components/ChatPanel';
import { TemplatesPanel } from './components/TemplatesPanel';
import { Account, Template, ChatMessage } from './types';
import { generateId, encryptApiKey, decryptApiKey } from './utils/crypto';
import { storage } from './utils/storage';

function App() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [currentAccountId, setCurrentAccountId] = useState<string | null>(null);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isAccountModalOpen, setIsAccountModalOpen] = useState(false);

  // Load data on mount
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [loadedAccounts, loadedTemplates] = await Promise.all([
        storage.getAccounts(),
        storage.getTemplates(),
      ]);
      setAccounts(loadedAccounts);
      setTemplates(loadedTemplates);
      
      // Set first account as current if none selected
      if (loadedAccounts.length > 0 && !currentAccountId) {
        setCurrentAccountId(loadedAccounts[0].id);
      }
    } catch (error) {
      console.error('Failed to load data:', error);
    }
  };

  const handleSaveAccount = async (account: Omit<Account, 'id' | 'createdAt' | 'updatedAt'>) => {
    try {
      const encryptedKey = await encryptApiKey(account.apiKey);
      const newAccount: Account = {
        ...account,
        id: generateId(),
        apiKey: encryptedKey,
        createdAt: Date.now(),
        updatedAt: Date.now(),
      };
      
      await storage.saveAccount(newAccount);
      setAccounts(prev => [...prev, newAccount]);
      if (!currentAccountId) {
        setCurrentAccountId(newAccount.id);
      }
      setIsAccountModalOpen(false);
    } catch (error) {
      console.error('Failed to save account:', error);
      alert('Failed to save account');
    }
  };

  const handleUpdateAccount = async (account: Account) => {
    try {
      const updatedAccount = {
        ...account,
        updatedAt: Date.now(),
      };
      await storage.saveAccount(updatedAccount);
      setAccounts(prev => prev.map(a => a.id === account.id ? updatedAccount : a));
      setIsAccountModalOpen(false);
    } catch (error) {
      console.error('Failed to update account:', error);
      alert('Failed to update account');
    }
  };

  const handleDeleteAccount = async (id: string) => {
    if (!confirm('Are you sure you want to delete this account?')) return;
    
    try {
      await storage.deleteAccount(id);
      setAccounts(prev => prev.filter(a => a.id !== id));
      if (currentAccountId === id) {
        setCurrentAccountId(null);
      }
    } catch (error) {
      console.error('Failed to delete account:', error);
    }
  };

  const handleSwitchAccount = (accountId: string) => {
    setCurrentAccountId(accountId);
    setMessages([]); // Clear chat when switching accounts
  };

  const handleSaveTemplate = async (template: Omit<Template, 'id' | 'createdAt' | 'updatedAt'>) => {
    const newTemplate: Template = {
      ...template,
      id: generateId(),
      createdAt: Date.now(),
      updatedAt: Date.now(),
    };
    
    await storage.saveTemplate(newTemplate);
    setTemplates(prev => [...prev, newTemplate]);
  };

  const handleUpdateTemplate = async (template: Template) => {
    const updatedTemplate = {
      ...template,
      updatedAt: Date.now(),
    };
    await storage.saveTemplate(updatedTemplate);
    setTemplates(prev => prev.map(t => t.id === template.id ? updatedTemplate : t));
  };

  const handleDeleteTemplate = async (id: string) => {
    await storage.deleteTemplate(id);
    setTemplates(prev => prev.filter(t => t.id !== id));
  };

  const handleInsertTemplate = (content: string) => {
    // Insert template content into chat input (handled in ChatPanel)
    const textarea = document.querySelector('textarea') as HTMLTextAreaElement;
    if (textarea) {
      textarea.value = content;
      textarea.focus();
    }
  };

  const handleSendMessage = async (content: string) => {
    if (!currentAccountId) {
      alert('Please select or add an account first');
      return;
    }

    const userMessage: ChatMessage = {
      id: generateId(),
      role: 'user',
      content,
      timestamp: Date.now(),
      accountId: currentAccountId,
    };
    
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const account = accounts.find(a => a.id === currentAccountId);
      if (!account) throw new Error('Account not found');
      
      const decryptedKey = await decryptApiKey(account.apiKey);
      
      // Send to API based on provider
      let response;
      if (account.provider === 'openai') {
        response = await fetch('https://api.openai.com/v1/chat/completions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${decryptedKey}`,
          },
          body: JSON.stringify({
            model: 'gpt-3.5-turbo',
            messages: [{ role: 'user', content }],
          }),
        });
        
        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.error?.message || 'API request failed');
        }
        
        const data = await response.json();
        const assistantMessage: ChatMessage = {
          id: generateId(),
          role: 'assistant',
          content: data.choices[0].message.content,
          timestamp: Date.now(),
          accountId: currentAccountId,
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        // Demo response for other providers
        setTimeout(() => {
          const assistantMessage: ChatMessage = {
            id: generateId(),
            role: 'assistant',
            content: `[${account.provider.toUpperCase()}] Demo response for: "${content}"\n\nNote: Full implementation for ${account.provider} requires additional setup.`,
            timestamp: Date.now(),
            accountId: currentAccountId,
          };
          setMessages(prev => [...prev, assistantMessage]);
        }, 1000);
      }
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: generateId(),
        role: 'assistant',
        content: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: Date.now(),
        accountId: currentAccountId,
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const currentAccount = accounts.find(a => a.id === currentAccountId);

  return (
    <div style={styles.app}>
      <Header 
        accounts={accounts}
        currentAccountId={currentAccountId}
        onSwitchAccount={handleSwitchAccount}
        onOpenAccountModal={() => setIsAccountModalOpen(true)}
        onOpenTemplateModal={() => {}}
        currentAccountName={currentAccount?.name}
      />
      
      <main style={styles.main}>
        <div style={styles.chatSection}>
          <ChatPanel 
            messages={messages} 
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
          />
        </div>
        
        <div style={styles.sidebar}>
          <TemplatesPanel 
            templates={templates}
            onInsertTemplate={handleInsertTemplate}
            onSaveTemplate={handleSaveTemplate}
            onUpdateTemplate={handleUpdateTemplate}
            onDeleteTemplate={handleDeleteTemplate}
            onOpenModal={() => {}}
          />
        </div>
      </main>

      {isAccountModalOpen && (
        <AccountModal
          accounts={accounts}
          onSave={handleSaveAccount}
          onUpdate={handleUpdateAccount}
          onDelete={handleDeleteAccount}
          onClose={() => setIsAccountModalOpen(false)}
        />
      )}
    </div>
  );
}

// Account Modal Component
function AccountModal({ 
  accounts, 
  onSave, 
  onUpdate, 
  onDelete,
  onClose 
}: { 
  accounts: Account[];
  onSave: (acc: Omit<Account, 'id' | 'createdAt' | 'updatedAt'>) => void;
  onUpdate: (acc: Account) => void;
  onDelete: (id: string) => void;
  onClose: () => void;
}) {
  const [editingAccount, setEditingAccount] = useState<Account | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    apiKey: '',
    provider: 'openai' as Account['provider'],
    baseUrl: '',
  });
  const [testingConnection, setTestingConnection] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingAccount) {
      onUpdate({ ...editingAccount, ...formData });
    } else {
      onSave(formData);
    }
  };

  const handleEdit = (account: Account) => {
    setEditingAccount(account);
    setFormData({
      name: account.name,
      apiKey: '', // Don't show encrypted key
      provider: account.provider,
      baseUrl: account.baseUrl || '',
    });
  };

  const handleTestConnection = async (account: Account) => {
    setTestingConnection(account.id);
    try {
      const decryptedKey = await decryptApiKey(account.apiKey);
      
      if (account.provider === 'openai') {
        const response = await fetch('https://api.openai.com/v1/models', {
          headers: {
            'Authorization': `Bearer ${decryptedKey}`,
          },
        });
        
        if (response.ok) {
          alert(`✓ Connection successful for "${account.name}"`);
        } else {
          const error = await response.json();
          alert(`✗ Connection failed: ${error.error?.message}`);
        }
      } else {
        alert(`Testing for ${account.provider} not implemented yet`);
      }
    } catch (error) {
      alert(`✗ Connection failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setTestingConnection(null);
    }
  };

  return (
    <div style={styles.modalOverlay} onClick={onClose}>
      <div style={styles.modal} onClick={e => e.stopPropagation()}>
        <h2 style={styles.modalTitle}>Manage Accounts</h2>
        
        <div style={styles.accountList}>
          {accounts.map(account => (
            <div key={account.id} style={styles.accountItem}>
              <div style={styles.accountInfo}>
                <strong>{account.name}</strong>
                <span style={styles.accountProvider}>{account.provider}</span>
              </div>
              <div style={styles.accountActions}>
                <button 
                  style={styles.smallButton}
                  onClick={() => handleTestConnection(account)}
                  disabled={testingConnection === account.id}
                >
                  {testingConnection === account.id ? 'Testing...' : 'Test'}
                </button>
                <button 
                  style={styles.smallButton}
                  onClick={() => handleEdit(account)}
                >
                  Edit
                </button>
                <button 
                  style={{...styles.smallButton, ...styles.deleteButton}}
                  onClick={() => onDelete(account.id)}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>

        <form onSubmit={handleSubmit} style={styles.form}>
          <h3>{editingAccount ? 'Edit Account' : 'Add New Account'}</h3>
          
          <input
            type="text"
            placeholder="Account Name"
            value={formData.name}
            onChange={e => setFormData({...formData, name: e.target.value})}
            style={styles.input}
            required
          />
          
          {!editingAccount && (
            <input
              type="password"
              placeholder="API Key"
              value={formData.apiKey}
              onChange={e => setFormData({...formData, apiKey: e.target.value})}
              style={styles.input}
              required={!editingAccount}
            />
          )}
          
          <select
            value={formData.provider}
            onChange={(e) => setFormData({...formData, provider: e.target.value as Account['provider']})}
            style={styles.select}
          >
            <option value="openai">OpenAI</option>
            <option value="anthropic">Anthropic</option>
            <option value="custom">Custom</option>
          </select>
          
          {formData.provider === 'custom' && (
            <input
              type="url"
              placeholder="Base URL (e.g., https://api.example.com)"
              value={formData.baseUrl}
              onChange={e => setFormData({...formData, baseUrl: e.target.value})}
              style={styles.input}
            />
          )}
          
          <div style={styles.modalActions}>
            <button type="submit" style={styles.primaryButton}>
              {editingAccount ? 'Update' : 'Add'} Account
            </button>
            {editingAccount && (
              <button 
                type="button" 
                style={styles.secondaryButton}
                onClick={() => {
                  setEditingAccount(null);
                  setFormData({ name: '', apiKey: '', provider: 'openai', baseUrl: '' });
                }}
              >
                Cancel
              </button>
            )}
            <button type="button" style={styles.secondaryButton} onClick={onClose}>
              Close
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

const styles: { [key: string]: React.CSSProperties } = {
  app: {
    minHeight: '100vh',
    background: '#f5f7fa',
  },
  main: {
    display: 'grid',
    gridTemplateColumns: '1fr 350px',
    gap: '20px',
    padding: '20px',
    maxWidth: '1400px',
    margin: '0 auto',
    height: 'calc(100vh - 70px)',
  },
  chatSection: {
    display: 'flex',
    flexDirection: 'column',
  },
  sidebar: {
    overflowY: 'auto',
  },
  modalOverlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'rgba(0,0,0,0.5)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
  },
  modal: {
    background: 'white',
    borderRadius: '12px',
    padding: '24px',
    width: '90%',
    maxWidth: '600px',
    maxHeight: '80vh',
    overflowY: 'auto',
  },
  modalTitle: {
    margin: '0 0 20px 0',
    fontSize: '20px',
    color: '#1a1a1a',
  },
  accountList: {
    marginBottom: '20px',
  },
  accountItem: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '12px',
    border: '1px solid #e0e0e0',
    borderRadius: '8px',
    marginBottom: '8px',
  },
  accountInfo: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  },
  accountProvider: {
    fontSize: '12px',
    color: '#666',
    background: '#f0f0f0',
    padding: '2px 8px',
    borderRadius: '4px',
    alignSelf: 'flex-start',
  },
  accountActions: {
    display: 'flex',
    gap: '8px',
  },
  smallButton: {
    padding: '4px 12px',
    fontSize: '12px',
    border: '1px solid #ddd',
    borderRadius: '6px',
    background: 'white',
    cursor: 'pointer',
  },
  deleteButton: {
    color: '#dc3545',
    borderColor: '#dc3545',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  input: {
    padding: '10px 12px',
    border: '1px solid #ddd',
    borderRadius: '8px',
    fontSize: '14px',
  },
  select: {
    padding: '10px 12px',
    border: '1px solid #ddd',
    borderRadius: '8px',
    fontSize: '14px',
    background: 'white',
  },
  modalActions: {
    display: 'flex',
    gap: '10px',
    marginTop: '10px',
  },
  primaryButton: {
    padding: '10px 20px',
    background: '#10a37f',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '14px',
    cursor: 'pointer',
    fontWeight: 500,
  },
  secondaryButton: {
    padding: '10px 20px',
    background: '#f0f0f0',
    color: '#333',
    border: 'none',
    borderRadius: '8px',
    fontSize: '14px',
    cursor: 'pointer',
  },
};

export default App;
