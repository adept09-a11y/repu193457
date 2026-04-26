import { useState, useEffect } from 'react';
import { Account, Template } from './types';
import { useAccounts, useTemplates } from './hooks';
import { AccountForm } from './AccountForm';
import { TemplateForm } from './TemplateForm';
import { Chat } from './Chat';

export default function App() {
  const { accounts, loading: accountsLoading, addAccount, updateAccount } = useAccounts();
  const { templates, loading: templatesLoading, addTemplate, updateTemplate, deleteTemplate, exportTemplates, importTemplates } = useTemplates();
  
  const [selectedAccountId, setSelectedAccountId] = useState<string>('');
  const [showAccountModal, setShowAccountModal] = useState(false);
  const [editingAccount, setEditingAccount] = useState<Account | undefined>();
  const [showTemplateModal, setShowTemplateModal] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<Template | undefined>();
  const [showShortcuts, setShowShortcuts] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Load master password state
  useEffect(() => {
    const initAuth = async () => {
      // For MVP, we'll skip the master password requirement
      // In production, you'd verify/set it here
    };
    initAuth();
  }, []);

  const selectedAccount = accounts.find(a => a.id === selectedAccountId) || null;

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const accountSelect = document.getElementById('account-select') as HTMLSelectElement;
        if (accountSelect) accountSelect.focus();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleSendMessage = async (prompt: string): Promise<string> => {
    if (!selectedAccount) throw new Error('No account selected');

    const endpoint = selectedAccount.provider === 'openai'
      ? (selectedAccount.baseUrl || 'https://api.openai.com/v1/chat/completions')
      : selectedAccount.provider === 'anthropic'
        ? 'https://api.anthropic.com/v1/messages'
        : selectedAccount.baseUrl || '';

    const headers: Record<string, string> = {
      'Content-Type': 'application/json'
    };

    if (selectedAccount.provider === 'anthropic') {
      headers['x-api-key'] = selectedAccount.apiKey;
      headers['anthropic-version'] = '2023-06-01';
    } else {
      headers['Authorization'] = `Bearer ${selectedAccount.apiKey}`;
    }

    const body = selectedAccount.provider === 'anthropic'
      ? {
          model: 'claude-3-haiku-20240307',
          max_tokens: 2048,
          messages: [{ role: 'user', content: prompt }]
        }
      : {
          model: 'gpt-3.5-turbo',
          messages: [{ role: 'user', content: prompt }]
        };

    const response = await fetch(endpoint, {
      method: 'POST',
      headers,
      body: JSON.stringify(body)
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.error?.message || `API Error: ${response.status}`);
    }

    const data = await response.json();
    
    if (selectedAccount.provider === 'anthropic') {
      return data.content[0].text;
    } else {
      return data.choices[0].message.content;
    }
  };

  const handleSaveAccount = async (account: Omit<Account, 'id'>) => {
    if (editingAccount) {
      await updateAccount(editingAccount.id, account);
    } else {
      await addAccount(account);
    }
    setShowAccountModal(false);
    setEditingAccount(undefined);
  };

  const handleSaveTemplate = async (template: Omit<Template, 'id'>) => {
    if (editingTemplate) {
      await updateTemplate(editingTemplate.id, template);
    } else {
      await addTemplate(template);
    }
    setShowTemplateModal(false);
    setEditingTemplate(undefined);
  };

  const insertTemplate = (template: Template) => {
    const textarea = document.querySelector('textarea');
    if (textarea) {
      textarea.value = template.content;
      textarea.dispatchEvent(new Event('input', { bubbles: true }));
      textarea.focus();
    }
  };

  const handleExportTemplates = async () => {
    const json = await exportTemplates();
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'templates.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleImportTemplates = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async (event) => {
      try {
        const json = event.target?.result as string;
        await importTemplates(json);
      } catch (err) {
        alert('Failed to import templates');
      }
    };
    reader.readAsText(file);
  };

  const filteredAccounts = accounts.filter(a => 
    a.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    a.provider.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (accountsLoading || templatesLoading) {
    return <div style={styles.loading}>Loading...</div>;
  }

  return (
    <div style={styles.app}>
      {/* Header */}
      <header style={styles.header}>
        <h1 style={styles.logo}>🤖 ChatGPT Interface</h1>
        
        <div style={styles.accountSection}>
          <label style={styles.label}>Account:</label>
          <select
            id="account-select"
            value={selectedAccountId}
            onChange={(e) => setSelectedAccountId(e.target.value)}
            style={styles.select}
          >
            <option value="">Select Account...</option>
            {accounts.map(account => (
              <option key={account.id} value={account.id}>
                {account.name} ({account.provider})
              </option>
            ))}
          </select>
          
          <button onClick={() => { setEditingAccount(undefined); setShowAccountModal(true); }} style={styles.button}>
            + Add
          </button>
        </div>

        <button onClick={() => setShowShortcuts(!showShortcuts)} style={styles.iconButton}>
          ⌨️
        </button>
      </header>

      {showShortcuts && (
        <div style={styles.shortcuts}>
          <h4>Keyboard Shortcuts</h4>
          <ul>
            <li><kbd>Ctrl/Cmd+K</kbd> - Quick account switcher</li>
            <li><kbd>Ctrl/Cmd+Enter</kbd> - Send message</li>
          </ul>
        </div>
      )}

      <div style={styles.main}>
        {/* Sidebar */}
        <aside style={styles.sidebar}>
          <div style={styles.section}>
            <div style={styles.sectionHeader}>
              <h3>Templates</h3>
              <div style={styles.sectionActions}>
                <button onClick={() => { setEditingTemplate(undefined); setShowTemplateModal(true); }} style={styles.smallButton}>+</button>
                <button onClick={handleExportTemplates} style={styles.smallButton}>⬇️</button>
                <label style={styles.smallButton}>
                  ⬆️
                  <input type="file" accept=".json" onChange={handleImportTemplates} style={{ display: 'none' }} />
                </label>
              </div>
            </div>

            {templates.length === 0 ? (
              <p style={styles.empty}>No templates yet</p>
            ) : (
              <div style={styles.templateList}>
                {templates.map(template => (
                  <div key={template.id} style={styles.templateItem}>
                    <div style={styles.templateInfo}>
                      <strong>{template.name}</strong>
                      {template.description && <small style={styles.templateDesc}>{template.description}</small>}
                    </div>
                    <div style={styles.templateActions}>
                      <button onClick={() => insertTemplate(template)} style={styles.tinyButton} title="Insert">
                        ➤
                      </button>
                      <button onClick={() => { setEditingTemplate(template); setShowTemplateModal(true); }} style={styles.tinyButton} title="Edit">
                        ✏️
                      </button>
                      <button onClick={() => deleteTemplate(template.id)} style={styles.tinyButton} title="Delete">
                        🗑️
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div style={styles.section}>
            <h3>All Accounts</h3>
            <input
              type="text"
              placeholder="Search accounts..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={styles.searchInput}
            />
            <div style={styles.accountList}>
              {filteredAccounts.map(account => (
                <div
                  key={account.id}
                  style={{
                    ...styles.accountItem,
                    ...(account.id === selectedAccountId ? styles.accountItemActive : {})
                  }}
                  onClick={() => setSelectedAccountId(account.id)}
                >
                  <span>{account.name}</span>
                  <span style={styles.accountProvider}>{account.provider}</span>
                </div>
              ))}
            </div>
          </div>
        </aside>

        {/* Main Chat Area */}
        <main style={styles.chatArea}>
          <Chat account={selectedAccount} onSendMessage={handleSendMessage} />
        </main>
      </div>

      {/* Account Modal */}
      {showAccountModal && (
        <div style={styles.modalOverlay} onClick={() => { setShowAccountModal(false); setEditingAccount(undefined); }}>
          <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
            <AccountForm
              account={editingAccount}
              onSave={handleSaveAccount}
              onCancel={() => { setShowAccountModal(false); setEditingAccount(undefined); }}
            />
          </div>
        </div>
      )}

      {/* Template Modal */}
      {showTemplateModal && (
        <div style={styles.modalOverlay} onClick={() => { setShowTemplateModal(false); setEditingTemplate(undefined); }}>
          <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
            <TemplateForm
              template={editingTemplate}
              onSave={handleSaveTemplate}
              onCancel={() => { setShowTemplateModal(false); setEditingTemplate(undefined); }}
            />
          </div>
        </div>
      )}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  app: {
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
    backgroundColor: '#1a1a1a',
    color: '#fff'
  },
  loading: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    height: '100vh',
    fontSize: '20px'
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    padding: '12px 20px',
    backgroundColor: '#2c2c2c',
    borderBottom: '1px solid #444',
    gap: '20px'
  },
  logo: {
    margin: 0,
    fontSize: '20px',
    fontWeight: 'bold'
  },
  accountSection: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    flex: 1
  },
  label: {
    fontSize: '14px',
    color: '#aaa'
  },
  select: {
    padding: '8px 12px',
    fontSize: '14px',
    border: '1px solid #444',
    borderRadius: '4px',
    backgroundColor: '#1a1a1a',
    color: '#fff',
    minWidth: '200px'
  },
  button: {
    padding: '8px 16px',
    backgroundColor: '#007bff',
    color: '#fff',
    borderRadius: '4px',
    border: 'none'
  },
  iconButton: {
    padding: '8px 12px',
    backgroundColor: 'transparent',
    border: '1px solid #444',
    borderRadius: '4px',
    fontSize: '16px'
  },
  shortcuts: {
    padding: '12px 20px',
    backgroundColor: '#2c2c2c',
    borderBottom: '1px solid #444'
  },
  main: {
    display: 'flex',
    flex: 1,
    overflow: 'hidden'
  },
  sidebar: {
    width: '300px',
    backgroundColor: '#242424',
    borderRight: '1px solid #444',
    overflowY: 'auto',
    padding: '16px'
  },
  section: {
    marginBottom: '24px'
  },
  sectionHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '12px'
  },
  sectionActions: {
    display: 'flex',
    gap: '4px'
  },
  smallButton: {
    padding: '4px 8px',
    backgroundColor: '#444',
    color: '#fff',
    borderRadius: '4px',
    border: 'none',
    fontSize: '14px',
    cursor: 'pointer'
  },
  tinyButton: {
    padding: '2px 6px',
    backgroundColor: 'transparent',
    border: 'none',
    fontSize: '12px',
    cursor: 'pointer',
    opacity: 0.7
  },
  empty: {
    color: '#888',
    fontSize: '14px',
    textAlign: 'center',
    padding: '20px 0'
  },
  templateList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px'
  },
  templateItem: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '8px',
    backgroundColor: '#2c2c2c',
    borderRadius: '4px'
  },
  templateInfo: {
    display: 'flex',
    flexDirection: 'column',
    gap: '2px'
  },
  templateDesc: {
    color: '#888',
    fontSize: '12px'
  },
  templateActions: {
    display: 'flex',
    gap: '4px'
  },
  searchInput: {
    width: '100%',
    padding: '8px',
    marginBottom: '8px',
    border: '1px solid #444',
    borderRadius: '4px',
    backgroundColor: '#1a1a1a',
    color: '#fff'
  },
  accountList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px'
  },
  accountItem: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '8px',
    backgroundColor: '#2c2c2c',
    borderRadius: '4px',
    cursor: 'pointer',
    transition: 'background-color 0.2s'
  },
  accountItemActive: {
    backgroundColor: '#007bff'
  },
  accountProvider: {
    fontSize: '12px',
    color: '#888',
    backgroundColor: '#444',
    padding: '2px 6px',
    borderRadius: '4px'
  },
  chatArea: {
    flex: 1,
    padding: '16px',
    overflow: 'hidden'
  },
  modalOverlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000
  },
  modal: {
    backgroundColor: '#2c2c2c',
    borderRadius: '8px',
    maxWidth: '500px',
    width: '90%',
    maxHeight: '90vh',
    overflow: 'auto'
  }
};
