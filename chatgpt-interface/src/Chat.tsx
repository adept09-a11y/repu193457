import { useState } from 'react';
import { Account, ChatMessage } from './types';

interface Props {
  account: Account | null;
  onSendMessage: (prompt: string) => Promise<string>;
}

export function Chat({ account, onSendMessage }: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || !account || loading) return;

    const userMessage = input.trim();
    setInput('');
    setLoading(true);
    setError('');

    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);

    try {
      const response = await onSendMessage(userMessage);
      setMessages(prev => [...prev, { role: 'assistant', content: response }]);
    } catch (err: any) {
      setError(err.message || 'Failed to send message');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      handleSubmit();
    }
  };

  if (!account) {
    return (
      <div style={styles.container}>
        <div style={styles.empty}>Select an account to start chatting</div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <span style={styles.accountBadge}>{account.name}</span>
        <span style={styles.provider}>{account.provider}</span>
      </div>

      <div style={styles.messages}>
        {messages.length === 0 ? (
          <div style={styles.empty}>Send a message to start the conversation</div>
        ) : (
          messages.map((msg, idx) => (
            <div key={idx} style={{ ...styles.message, ...(msg.role === 'user' ? styles.userMessage : styles.assistantMessage) }}>
              <div style={styles.messageRole}>{msg.role === 'user' ? 'You' : 'Assistant'}</div>
              <div style={styles.messageContent}>{msg.content}</div>
            </div>
          ))
        )}
        {loading && (
          <div style={{ ...styles.message, ...styles.assistantMessage }}>
            <div style={styles.messageRole}>Assistant</div>
            <div style={styles.loading}>Thinking...</div>
          </div>
        )}
      </div>

      {error && <div style={styles.error}>{error}</div>}

      <form onSubmit={handleSubmit} style={styles.form}>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message... (Ctrl/Cmd+Enter to send)"
          style={styles.textarea}
          rows={3}
        />
        <button type="submit" disabled={!input.trim() || loading} style={styles.sendButton}>
          Send
        </button>
      </form>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    backgroundColor: '#1a1a1a',
    borderRadius: '8px',
    overflow: 'hidden'
  },
  header: {
    padding: '12px 16px',
    backgroundColor: '#2c2c2c',
    borderBottom: '1px solid #444',
    display: 'flex',
    gap: '12px',
    alignItems: 'center'
  },
  accountBadge: {
    fontWeight: 'bold',
    color: '#fff'
  },
  provider: {
    fontSize: '12px',
    color: '#888',
    backgroundColor: '#444',
    padding: '2px 8px',
    borderRadius: '4px'
  },
  messages: {
    flex: 1,
    overflowY: 'auto',
    padding: '16px',
    display: 'flex',
    flexDirection: 'column',
    gap: '16px'
  },
  message: {
    maxWidth: '80%',
    padding: '12px 16px',
    borderRadius: '8px',
    alignSelf: 'flex-start'
  },
  userMessage: {
    backgroundColor: '#007bff',
    color: '#fff',
    alignSelf: 'flex-end'
  },
  assistantMessage: {
    backgroundColor: '#2c2c2c',
    color: '#fff'
  },
  messageRole: {
    fontSize: '12px',
    marginBottom: '4px',
    opacity: 0.7
  },
  messageContent: {
    whiteSpace: 'pre-wrap',
    wordBreak: 'break-word'
  },
  empty: {
    textAlign: 'center',
    color: '#888',
    marginTop: '40px'
  },
  loading: {
    color: '#888',
    fontStyle: 'italic'
  },
  error: {
    padding: '8px 16px',
    backgroundColor: '#f8d7da',
    color: '#721c24',
    margin: '0 16px',
    borderRadius: '4px'
  },
  form: {
    padding: '16px',
    backgroundColor: '#2c2c2c',
    borderTop: '1px solid #444',
    display: 'flex',
    gap: '8px'
  },
  textarea: {
    flex: 1,
    resize: 'none',
    padding: '12px',
    border: '1px solid #444',
    borderRadius: '4px',
    backgroundColor: '#1a1a1a',
    color: '#fff',
    fontFamily: 'inherit'
  },
  sendButton: {
    padding: '12px 24px',
    backgroundColor: '#007bff',
    color: '#fff',
    borderRadius: '4px',
    border: 'none',
    fontWeight: 'bold',
    minWidth: '80px'
  }
};
