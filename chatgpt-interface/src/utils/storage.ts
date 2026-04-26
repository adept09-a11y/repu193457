import localforage from 'localforage';
import { Account, Template } from '../types';

// Initialize localforage instances
const accountsDb = localforage.createInstance({
  name: 'chatgpt-accounts',
  storeName: 'accounts',
});

const templatesDb = localforage.createInstance({
  name: 'chatgpt-templates',
  storeName: 'templates',
});

export const storage = {
  // Accounts
  async getAccounts(): Promise<Account[]> {
    const accounts: Account[] = [];
    await accountsDb.iterate((value: Account) => {
      accounts.push(value);
    });
    return accounts.sort((a, b) => b.createdAt - a.createdAt);
  },

  async saveAccount(account: Account): Promise<void> {
    await accountsDb.setItem(account.id, account);
  },

  async deleteAccount(id: string): Promise<void> {
    await accountsDb.removeItem(id);
  },

  async getAccount(id: string): Promise<Account | null> {
    return await accountsDb.getItem(id);
  },

  // Templates
  async getTemplates(): Promise<Template[]> {
    const templates: Template[] = [];
    await templatesDb.iterate((value: Template) => {
      templates.push(value);
    });
    return templates.sort((a, b) => b.createdAt - a.createdAt);
  },

  async saveTemplate(template: Template): Promise<void> {
    await templatesDb.setItem(template.id, template);
  },

  async deleteTemplate(id: string): Promise<void> {
    await templatesDb.removeItem(id);
  },

  async clearAll(): Promise<void> {
    await accountsDb.clear();
    await templatesDb.clear();
  },
};
