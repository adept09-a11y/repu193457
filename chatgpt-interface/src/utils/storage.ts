import localforage from 'localforage';
import { User, Template } from '../types';

const usersDb = localforage.createInstance({ name: 'users' });
const templatesDb = localforage.createInstance({ name: 'templates' });

export async function createUser(username: string, password: string): Promise<User | null> {
  // Check if user exists
  const existingUser = await usersDb.getItem<User>(username.toLowerCase());
  if (existingUser) {
    return null;
  }

  const salt = await import('./crypto').then(m => m.generateSalt());
  const passwordHash = await import('./crypto').then(m => m.hashPassword(password, salt));
  
  const user: User = {
    id: await import('./crypto').then(m => m.generateId()),
    username,
    passwordHash,
    salt,
    createdAt: Date.now(),
  };

  await usersDb.setItem(username.toLowerCase(), user);
  return user;
}

export async function authenticateUser(username: string, password: string): Promise<User | null> {
  const user = await usersDb.getItem<User>(username.toLowerCase());
  if (!user) {
    return null;
  }

  const isValid = await import('./crypto').then(m => m.verifyPassword(password, user.salt, user.passwordHash));
  if (!isValid) {
    return null;
  }

  return user;
}

export async function getUserByUsername(username: string): Promise<User | null> {
  return await usersDb.getItem<User>(username.toLowerCase());
}

// Template operations
export async function saveTemplate(template: Template): Promise<void> {
  await templatesDb.setItem(template.id, template);
}

export async function getTemplatesForUser(userId: string): Promise<Template[]> {
  const templates: Template[] = [];
  await templatesDb.iterate((value: Template) => {
    if (value.userId === userId) {
      templates.push(value);
    }
  });
  return templates;
}

export async function deleteTemplate(templateId: string): Promise<void> {
  await templatesDb.removeItem(templateId);
}

export async function exportTemplates(userId: string): Promise<string> {
  const templates = await getTemplatesForUser(userId);
  return JSON.stringify(templates, null, 2);
}

export async function importTemplates(userId: string, json: string): Promise<number> {
  try {
    const templates: Omit<Template, 'userId'>[] = JSON.parse(json);
    let count = 0;
    
    for (const template of templates) {
      const newTemplate: Template = {
        ...template,
        userId,
        id: await import('./crypto').then(m => m.generateId()),
        updatedAt: Date.now(),
      };
      await saveTemplate(newTemplate);
      count++;
    }
    
    return count;
  } catch (error) {
    console.error('Failed to import templates:', error);
    return 0;
  }
}
