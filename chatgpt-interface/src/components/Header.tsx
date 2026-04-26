import React from 'react';
import { User } from '../types';

interface HeaderProps {
  user: User;
  onLogout: () => void;
}

export const Header: React.FC<HeaderProps> = ({ user, onLogout }) => {
  return (
    <header style={styles.header}>
      <div style={styles.logo}>
        <span style={styles.icon}>🤖</span>
        <h1 style={styles.title}>ChatGPT Interface</h1>
      </div>
      
      <div style={styles.userInfo}>
        <span style={styles.username}>👤 {user.username}</span>
        <button onClick={onLogout} style={styles.logoutButton}>
          Logout
        </button>
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
  userInfo: {
    display: 'flex',
    alignItems: 'center',
    gap: '15px',
  },
  username: {
    color: '#555',
    fontWeight: '500',
  },
  logoutButton: {
    padding: '8px 16px',
    background: '#f0f0f0',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontWeight: '500',
    color: '#666',
    transition: 'background 0.2s',
  },
};
