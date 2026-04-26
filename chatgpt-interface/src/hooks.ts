import { useState, useEffect, useCallback } from 'react';
import { Account, Template } from './types';
import { accountsDB, templatesDB, encryptApiKey, decryptApiKey } from './db';

export function useAccounts() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);

  const loadAccounts = useCallback(async () => {
    try {
      const keys = await accountsDB.keys();
      const loadedAccounts: Account[] = [];
      
      for (const key of keys) {
        const encryptedAccount = await accountsDB.getItem<{
          id: string;
          name: string;
          provider: 'openai' | 'anthropic' | 'custom';
          apiKey: string;
          baseUrl?: string;
        }>(key);
        
        if (encryptedAccount) {
          try {
            const decryptedApiKey = await decryptApiKey(encryptedAccount.apiKey);
            loadedAccounts.push({
              ...encryptedAccount,
              apiKey: decryptedApiKey
            });
          } catch (e) {
            console.error('Failed to decrypt API key for account:', key);
          }
        }
      }
      
      setAccounts(loadedAccounts);
    } catch (error) {
      console.error('Failed to load accounts:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAccounts();
  }, [loadAccounts]);

  const addAccount = async (account: Omit<Account, 'id'>) => {
    const id = crypto.randomUUID();
    const encryptedApiKey = await encryptApiKey(account.apiKey);
    
    await accountsDB.setItem(id, {
      ...account,
      apiKey: encryptedApiKey,
      id
    });
    
    await loadAccounts();
    return id;
  };

  const updateAccount = async (id: string, updates: Partial<Account>) => {
    const existing = await accountsDB.getItem<Account>(id);
    if (!existing) throw new Error('Account not found');

    const encryptedApiKey = updates.apiKey 
      ? await encryptApiKey(updates.apiKey)
      : existing.apiKey;

    await accountsDB.setItem(id, {
      ...existing,
      ...updates,
      apiKey: encryptedApiKey,
      id
    });

    await loadAccounts();
  };

  const deleteAccount = async (id: string) => {
    await accountsDB.removeItem(id);
    await loadAccounts();
  };

  return { accounts, loading, addAccount, updateAccount, deleteAccount, refresh: loadAccounts };
}

export function useTemplates() {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);

  const loadTemplates = useCallback(async () => {
    try {
      const items: Template[] = [];
      await templatesDB.iterate((value: Template) => {
        items.push(value);
      });
      setTemplates(items);
    } catch (error) {
      console.error('Failed to load templates:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadTemplates();
  }, [loadTemplates]);

  const addTemplate = async (template: Omit<Template, 'id'>) => {
    const id = crypto.randomUUID();
    const newTemplate: Template = { ...template, id };
    
    await templatesDB.setItem(id, newTemplate);
    await loadTemplates();
    return id;
  };

  const updateTemplate = async (id: string, updates: Partial<Template>) => {
    const existing = await templatesDB.getItem<Template>(id);
    if (!existing) throw new Error('Template not found');

    await templatesDB.setItem(id, { ...existing, ...updates, id });
    await loadTemplates();
  };

  const deleteTemplate = async (id: string) => {
    await templatesDB.removeItem(id);
    await loadTemplates();
  };

  const exportTemplates = async (): Promise<string> => {
    const items: Template[] = [];
    await templatesDB.iterate((value: Template) => {
      items.push(value);
    });
    return JSON.stringify(items, null, 2);
  };

  const importTemplates = async (json: string) => {
    const imported: Template[] = JSON.parse(json);
    for (const template of imported) {
      const id = crypto.randomUUID();
      await templatesDB.setItem(id, { ...template, id });
    }
    await loadTemplates();
  };

  return { 
    templates, 
    loading, 
    addTemplate, 
    updateTemplate, 
    deleteTemplate, 
    exportTemplates,
    importTemplates,
    refresh: loadTemplates
  };
}
