import { useState } from 'react';
import { Account } from './types';

interface Props {
  account?: Account;
  onSave: (account: Omit<Account, 'id'>) => Promise<void>;
  onCancel: () => void;
}

export function AccountForm({ account, onSave, onCancel }: Props) {
  const [name, setName] = useState(account?.name || '');
  const [provider, setProvider] = useState<'openai' | 'anthropic' | 'custom'>(
    account?.provider || 'openai'
  );
  const [apiKey, setApiKey] = useState(account?.apiKey || '');
  const [baseUrl, setBaseUrl] = useState(account?.baseUrl || '');
  const [error, setError] = useState('');
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !apiKey.trim()) {
      setError('Name and API Key are required');
      return;
    }

    try {
      await onSave({ name: name.trim(), provider, apiKey: apiKey.trim(), baseUrl: baseUrl.trim() || undefined });
    } catch (err) {
      setError('Failed to save account');
    }
  };

  const testConnection = async () => {
    if (!apiKey.trim()) {
      setError('API Key is required for testing');
      return;
    }

    setTesting(true);
    setTestResult(null);

    try {
      const endpoint = provider === 'openai' 
        ? (baseUrl || 'https://api.openai.com/v1/chat/completions')
        : provider === 'anthropic'
          ? 'https://api.anthropic.com/v1/messages'
          : baseUrl || '';

      if (!endpoint) {
        throw new Error('Base URL required for custom provider');
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          [provider === 'anthropic' ? 'x-api-key' : 'Authorization']: 
            provider === 'anthropic' ? apiKey : `Bearer ${apiKey}`
        },
        body: JSON.stringify(
          provider === 'anthropic' 
            ? { model: 'claude-3-haiku-20240307', max_tokens: 1, messages: [{ role: 'user', content: 'test' }] }
            : { model: 'gpt-3.5-turbo', messages: [{ role: 'user', content: 'test' }], max_tokens: 1 }
        )
      });

      if (response.ok || response.status === 400) {
        setTestResult({ success: true, message: 'Connection successful!' });
      } else {
        const error = await response.json().catch(() => ({}));
        setTestResult({ 
          success: false, 
          message: `Error: ${response.status} - ${error.error?.message || 'Unknown error'}` 
        });
      }
    } catch (err: any) {
      setTestResult({ success: false, message: `Connection failed: ${err.message}` });
    } finally {
      setTesting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={styles.form}>
      <h3>{account ? 'Edit Account' : 'Add Account'}</h3>
      
      {error && <div style={styles.error}>{error}</div>}
      {testResult && (
        <div style={{ ...styles.testResult, backgroundColor: testResult.success ? '#d4edda' : '#f8d7da' }}>
          {testResult.message}
        </div>
      )}

      <div style={styles.field}>
        <label>Name</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="My Account"
          style={styles.input}
        />
      </div>

      <div style={styles.field}>
        <label>Provider</label>
        <select value={provider} onChange={(e) => setProvider(e.target.value as any)} style={styles.input}>
          <option value="openai">OpenAI</option>
          <option value="anthropic">Anthropic</option>
          <option value="custom">Custom</option>
        </select>
      </div>

      <div style={styles.field}>
        <label>API Key</label>
        <input
          type="password"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          placeholder="sk-..."
          style={styles.input}
        />
      </div>

      {provider === 'custom' && (
        <div style={styles.field}>
          <label>Base URL</label>
          <input
            type="url"
            value={baseUrl}
            onChange={(e) => setBaseUrl(e.target.value)}
            placeholder="https://api.example.com/v1"
            style={styles.input}
          />
        </div>
      )}

      <div style={styles.buttons}>
        <button type="button" onClick={testConnection} disabled={testing} style={styles.testButton}>
          {testing ? 'Testing...' : 'Test Connection'}
        </button>
        <button type="submit" style={styles.primaryButton}>Save</button>
        <button type="button" onClick={onCancel} style={styles.button}>Cancel</button>
      </div>
    </form>
  );
}

const styles: Record<string, React.CSSProperties> = {
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
    padding: '20px',
    backgroundColor: '#2c2c2c',
    borderRadius: '8px'
  },
  field: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px'
  },
  input: {
    padding: '8px 12px',
    fontSize: '14px',
    border: '1px solid #444',
    borderRadius: '4px',
    backgroundColor: '#1a1a1a',
    color: '#fff'
  },
  buttons: {
    display: 'flex',
    gap: '8px',
    marginTop: '8px'
  },
  button: {
    padding: '8px 16px',
    backgroundColor: '#444',
    color: '#fff',
    borderRadius: '4px',
    border: 'none'
  },
  primaryButton: {
    padding: '8px 16px',
    backgroundColor: '#007bff',
    color: '#fff',
    borderRadius: '4px',
    border: 'none'
  },
  testButton: {
    padding: '8px 16px',
    backgroundColor: '#28a745',
    color: '#fff',
    borderRadius: '4px',
    border: 'none'
  },
  error: {
    padding: '8px',
    backgroundColor: '#f8d7da',
    color: '#721c24',
    borderRadius: '4px',
    fontSize: '14px'
  },
  testResult: {
    padding: '8px',
    borderRadius: '4px',
    fontSize: '14px'
  }
};
