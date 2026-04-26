export interface Account {
  id: string;
  name: string;
  apiKey: string; // Encrypted
  provider: 'openai' | 'anthropic' | 'custom';
  baseUrl?: string;
  createdAt: number;
  updatedAt: number;
}

export interface Template {
  id: string;
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
  accountId?: string;
}

export interface AppState {
  accounts: Account[];
  currentAccountId: string | null;
  templates: Template[];
  currentChat: ChatMessage[];
  isAccountModalOpen: boolean;
  isTemplateModalOpen: boolean;
}
