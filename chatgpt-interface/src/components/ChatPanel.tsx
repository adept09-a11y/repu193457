import React, { useState } from 'react';
import { ChatMessage } from '../types';

interface ChatPanelProps {
  onSendMessage: (message: string) => void;
  messages: ChatMessage[];
  isLoading: boolean;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({ onSendMessage, messages, isLoading }) => {
  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      handleSubmit(e);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.messagesContainer}>
        {messages.length === 0 ? (
          <div style={styles.empty}>
            <p>👋 Start a conversation!</p>
            <p style={styles.hint}>Press Ctrl+Enter to send</p>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              style={{
                ...styles.message,
                ...(msg.role === 'user' ? styles.userMessage : styles.assistantMessage),
              }}
            >
              <div style={styles.messageRole}>
                {msg.role === 'user' ? '👤 You' : '🤖 Assistant'}
              </div>
              <div style={styles.messageContent}>{msg.content}</div>
            </div>
          ))
        )}
        {isLoading && (
          <div style={{ ...styles.message, ...styles.assistantMessage }}>
            <div style={styles.messageRole}>🤖 Assistant</div>
            <div style={styles.loading}>Thinking...</div>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} style={styles.form}>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message... (Ctrl+Enter to send)"
          style={styles.textarea}
          rows={3}
          disabled={isLoading}
        />
        <button type="submit" style={styles.sendButton} disabled={!input.trim() || isLoading}>
          {isLoading ? '⏳' : '➤ Send'}
        </button>
      </form>
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    background: 'white',
    borderRadius: '12px',
    display: 'flex',
    flexDirection: 'column',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    overflow: 'hidden',
    height: '100%',
  },
  messagesContainer: {
    flex: 1,
    overflowY: 'auto',
    padding: '20px',
    minHeight: '300px',
    maxHeight: '500px',
  },
  empty: {
    textAlign: 'center',
    color: '#999',
    padding: '60px 20px',
  },
  hint: {
    fontSize: '14px',
    marginTop: '10px',
  },
  message: {
    marginBottom: '16px',
    padding: '15px',
    borderRadius: '12px',
    maxWidth: '85%',
  },
  userMessage: {
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
    marginLeft: 'auto',
  },
  assistantMessage: {
    background: '#f5f5f5',
    color: '#333',
  },
  messageRole: {
    fontSize: '12px',
    fontWeight: '600',
    marginBottom: '8px',
    opacity: 0.8,
  },
  messageContent: {
    fontSize: '15px',
    lineHeight: 1.5,
    whiteSpace: 'pre-wrap',
    wordBreak: 'break-word',
  },
  loading: {
    fontStyle: 'italic',
    color: '#666',
  },
  form: {
    display: 'flex',
    gap: '12px',
    padding: '20px',
    borderTop: '1px solid #eee',
    background: '#fafafa',
  },
  textarea: {
    flex: 1,
    padding: '12px 16px',
    border: '2px solid #e0e0e0',
    borderRadius: '8px',
    fontSize: '15px',
    resize: 'none',
    fontFamily: 'inherit',
    outline: 'none',
    transition: 'border-color 0.2s',
  },
  sendButton: {
    padding: '12px 24px',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '15px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'transform 0.2s, opacity 0.2s',
    minWidth: '100px',
  },
};
