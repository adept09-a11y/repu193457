import React, { useState } from 'react';
import { Account } from '../types';

interface HeaderProps {
  accounts: Account[];
  currentAccountId: string | null;
  onSwitchAccount: (accountId: string) => void;
  onOpenAccountModal: () => void;
  onOpenTemplateModal: () => void;
  currentAccountName?: string;
}

export const Header: React.FC<HeaderProps> = ({ 
  accounts, 
  currentAccountId, 
  onSwitchAccount,
  onOpenAccountModal,
  onOpenTemplateModal,
  currentAccountName 
}) => {
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Keyboard shortcut Ctrl/Cmd+K
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setSearchOpen(prev => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const filteredAccounts = accounts.filter(acc => 
    acc.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    acc.provider.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <header style={styles.header}>
      <div style={styles.logo}>
        <span style={styles.icon}>🤖</span>
        <h1 style={styles.title}>ChatGPT Multi-Account</h1>
      </div>
      
      <div style={styles.controls}>
        {/* Account Selector */}
        <div style={styles.accountSelector}>
          <label style={styles.label}>Account:</label>
          <select 
            value={currentAccountId || ''}
            onChange={(e) => onSwitchAccount(e.target.value)}
            style={styles.select}
          >
            {accounts.length === 0 ? (
              <option value="">No accounts</option>
            ) : (
              accounts.map(acc => (
                <option key={acc.id} value={acc.id}>
                  {acc.name} ({acc.provider})
                </option>
              ))
            )}
          </select>
          <button onClick={onOpenAccountModal} style={styles.manageButton}>
            Manage
          </button>
        </div>

        {/* Quick Account Switcher (Ctrl+K) */}
        <div style={styles.quickSwitcher}>
          <button 
            onClick={() => setSearchOpen(!searchOpen)}
            style={styles.quickSwitchButton}
            title="Ctrl/Cmd+K"
          >
            ⚡ Quick Switch
          </button>
          
          {searchOpen && (
            <div style={styles.searchDropdown}>
              <input
                type="text"
                placeholder="Search accounts... (Esc to close)"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Escape') setSearchOpen(false);
                }}
                style={styles.searchInput}
                autoFocus
              />
              <div style={styles.searchResults}>
                {filteredAccounts.map(acc => (
                  <button
                    key={acc.id}
                    onClick={() => {
                      onSwitchAccount(acc.id);
                      setSearchOpen(false);
                      setSearchQuery('');
                    }}
                    style={{
                      ...styles.searchResult,
                      background: acc.id === currentAccountId ? '#e8f5e9' : 'transparent',
                    }}
                  >
                    <span>{acc.name}</span>
                    <span style={styles.providerTag}>{acc.provider}</span>
                  </button>
                ))}
                {filteredAccounts.length === 0 && (
                  <div style={styles.noResults}>No accounts found</div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Templates Button */}
        <button onClick={onOpenTemplateModal} style={styles.templatesButton}>
          📝 Templates
        </button>

        {/* Current Account Display */}
        {currentAccountName && (
          <div style={styles.currentAccount}>
            <span style={styles.statusDot}>●</span>
            <span>{currentAccountName}</span>
          </div>
        )}
      </div>
    </header>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  header: {
    background: 'white',
    padding: '15px 30px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    position: 'sticky',
    top: 0,
    zIndex: 100,
  },
  logo: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  icon: {
    fontSize: '32px',
  },
  title: {
    margin: 0,
    fontSize: '24px',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
  },
  controls: {
    display: 'flex',
    alignItems: 'center',
    gap: '20px',
  },
  accountSelector: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  label: {
    fontSize: '14px',
    color: '#666',
    fontWeight: '500',
  },
  select: {
    padding: '8px 12px',
    border: '1px solid #ddd',
    borderRadius: '6px',
    fontSize: '14px',
    background: 'white',
    minWidth: '200px',
  },
  manageButton: {
    padding: '8px 12px',
    background: '#667eea',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '13px',
    fontWeight: '500',
  },
  quickSwitcher: {
    position: 'relative',
  },
  quickSwitchButton: {
    padding: '8px 16px',
    background: '#f0f0f0',
    border: '1px solid #ddd',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '13px',
    fontWeight: '500',
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
  },
  searchDropdown: {
    position: 'absolute',
    top: '100%',
    right: 0,
    marginTop: '8px',
    background: 'white',
    border: '1px solid #ddd',
    borderRadius: '8px',
    boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
    width: '300px',
    zIndex: 1000,
    overflow: 'hidden',
  },
  searchInput: {
    width: '100%',
    padding: '12px',
    border: 'none',
    borderBottom: '1px solid #eee',
    fontSize: '14px',
    outline: 'none',
    boxSizing: 'border-box',
  },
  searchResults: {
    maxHeight: '300px',
    overflowY: 'auto',
  },
  searchResult: {
    width: '100%',
    padding: '10px 12px',
    border: 'none',
    background: 'transparent',
    textAlign: 'left',
    cursor: 'pointer',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    fontSize: '14px',
    transition: 'background 0.15s',
  },
  providerTag: {
    fontSize: '11px',
    padding: '2px 6px',
    background: '#f0f0f0',
    borderRadius: '4px',
    color: '#666',
  },
  noResults: {
    padding: '12px',
    textAlign: 'center',
    color: '#999',
    fontSize: '14px',
  },
  templatesButton: {
    padding: '8px 16px',
    background: '#10a37f',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '13px',
    fontWeight: '500',
  },
  currentAccount: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    fontSize: '13px',
    color: '#666',
    padding: '6px 12px',
    background: '#f5f7fa',
    borderRadius: '6px',
  },
  statusDot: {
    color: '#10a37f',
    fontSize: '10px',
  },
};
