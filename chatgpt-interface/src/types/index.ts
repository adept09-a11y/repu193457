export interface User {
  id: string;
  username: string;
  passwordHash: string;
  salt: string;
  createdAt: number;
}

export interface Template {
  id: string;
  userId: string;
  name: string;
  content: string;
  createdAt: number;
  updatedAt: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

export interface AppState {
  currentUser: User | null;
  templates: Template[];
  currentChat: ChatMessage[];
}
