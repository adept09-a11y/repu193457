import React, { useState, useEffect } from 'react';
import { Auth } from './components/Auth';
import { Header } from './components/Header';
import { ChatPanel } from './components/ChatPanel';
import { TemplatesPanel } from './components/TemplatesPanel';
import { User, ChatMessage } from './types';
import { generateId } from './utils/crypto';

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Check for existing session on mount
  useEffect(() => {
    const checkSession = async () => {
      const savedUser = sessionStorage.getItem('currentUser');
      if (savedUser) {
        try {
          setUser(JSON.parse(savedUser));
        } catch (e) {
          sessionStorage.removeItem('currentUser');
        }
      }
    };
    checkSession();
  }, []);

  const handleLogin = (loggedInUser: User) => {
    setUser(loggedInUser);
    sessionStorage.setItem('currentUser', JSON.stringify(loggedInUser));
  };

  const handleLogout = () => {
    setUser(null);
    setMessages([]);
    sessionStorage.removeItem('currentUser');
  };

  const handleSendMessage = async (content: string) => {
    // Add user message
    const userMessage: ChatMessage = {
      id: generateId(),
      role: 'user',
      content,
      timestamp: Date.now(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    // Simulate API response (in real app, this would call the API)
    setTimeout(() => {
      const assistantMessage: ChatMessage = {
        id: generateId(),
        role: 'assistant',
        content: `This is a demo response. In a real application, this would connect to an AI API.\n\nYour message: "${content}"`,
        timestamp: Date.now(),
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      setIsLoading(false);
    }, 1500);
  };

  const handleInsertTemplate = (templateContent: string) => {
    // In a real app, you'd insert this into the chat input
    alert(`Template inserted:\n\n${templateContent}\n\n(You can customize the placeholders like {{name}} before sending)`);
  };

  if (!user) {
    return <Auth onLogin={handleLogin} />;
  }

  return (
    <div style={styles.app}>
      <Header user={user} onLogout={handleLogout} />
      
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
            userId={user.id}
            onInsertTemplate={handleInsertTemplate}
          />
        </div>
      </main>
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
};

export default App;
