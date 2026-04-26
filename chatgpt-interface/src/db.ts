import localforage from 'localforage';

export const accountsDB = localforage.createInstance({
  name: 'chatgpt-interface',
  storeName: 'accounts'
});

export const templatesDB = localforage.createInstance({
  name: 'chatgpt-interface',
  storeName: 'templates'
});

export const settingsDB = localforage.createInstance({
  name: 'chatgpt-interface',
  storeName: 'settings'
});

// Web Crypto API helpers for encryption
const encoder = new TextEncoder();
const decoder = new TextDecoder();

let masterKey: CryptoKey | null = null;

export async function deriveKey(password: string): Promise<CryptoKey> {
  const keyMaterial = await crypto.subtle.importKey(
    'raw',
    encoder.encode(password),
    { name: 'PBKDF2' },
    false,
    ['deriveBits', 'deriveKey']
  );

  const salt = encoder.encode('chatgpt-interface-salt');

  return crypto.subtle.deriveKey(
    {
      name: 'PBKDF2',
      salt,
      iterations: 100000,
      hash: 'SHA-256'
    },
    keyMaterial,
    { name: 'AES-GCM', length: 256 },
    false,
    ['encrypt', 'decrypt']
  );
}

export async function setMasterPassword(password: string): Promise<void> {
  masterKey = await deriveKey(password);
  await settingsDB.setItem('masterPasswordSet', true);
}

export async function verifyMasterPassword(password: string): Promise<boolean> {
  try {
    const testKey = await deriveKey(password);
    // Try to decrypt a test value
    const encrypted = await encrypt('test', testKey);
    const decrypted = await decrypt(encrypted, testKey);
    return decrypted === 'test';
  } catch {
    return false;
  }
}

export async function encrypt(data: string, key?: CryptoKey): Promise<string> {
  const cryptoKey = key || masterKey;
  if (!cryptoKey) throw new Error('Master key not set');

  const iv = crypto.getRandomValues(new Uint8Array(12));
  const encrypted = await crypto.subtle.encrypt(
    { name: 'AES-GCM', iv },
    cryptoKey,
    encoder.encode(data)
  );

  const combined = new Uint8Array(iv.length + encrypted.byteLength);
  combined.set(iv, 0);
  combined.set(new Uint8Array(encrypted), iv.length);

  return btoa(String.fromCharCode(...combined));
}

export async function decrypt(encryptedData: string, key?: CryptoKey): Promise<string> {
  const cryptoKey = key || masterKey;
  if (!cryptoKey) throw new Error('Master key not set');

  const combined = Uint8Array.from(atob(encryptedData), c => c.charCodeAt(0));
  const iv = combined.slice(0, 12);
  const data = combined.slice(12);

  const decrypted = await crypto.subtle.decrypt(
    { name: 'AES-GCM', iv },
    cryptoKey,
    data
  );

  return decoder.decode(decrypted);
}

export async function encryptApiKey(apiKey: string): Promise<string> {
  return encrypt(apiKey);
}

export async function decryptApiKey(encryptedApiKey: string): Promise<string> {
  return decrypt(encryptedApiKey);
}
