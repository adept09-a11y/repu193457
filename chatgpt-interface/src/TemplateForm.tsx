import { useState } from 'react';
import { Template } from './types';

interface Props {
  template?: Template;
  onSave: (template: Omit<Template, 'id'>) => Promise<void>;
  onCancel: () => void;
}

export function TemplateForm({ template, onSave, onCancel }: Props) {
  const [name, setName] = useState(template?.name || '');
  const [content, setContent] = useState(template?.content || '');
  const [description, setDescription] = useState(template?.description || '');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !content.trim()) {
      setError('Name and Content are required');
      return;
    }

    try {
      await onSave({ 
        name: name.trim(), 
        content: content.trim(), 
        description: description.trim() || undefined 
      });
    } catch (err) {
      setError('Failed to save template');
    }
  };

  return (
    <form onSubmit={handleSubmit} style={styles.form}>
      <h3>{template ? 'Edit Template' : 'Add Template'}</h3>
      
      {error && <div style={styles.error}>{error}</div>}

      <div style={styles.field}>
        <label>Name</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Code Review"
          style={styles.input}
        />
      </div>

      <div style={styles.field}>
        <label>Description (optional)</label>
        <input
          type="text"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Review code for best practices"
          style={styles.input}
        />
      </div>

      <div style={styles.field}>
        <label>Content (use {'{{variable}}'} for placeholders)</label>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Review the following code:\n\n{{code}}"
          style={{ ...styles.input, minHeight: '150px', fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}
        />
      </div>

      <div style={styles.buttons}>
        <button type="submit" style={styles.primaryButton}>Save</button>
        <button type="button" onClick={onCancel} style={styles.button}>Cancel</button>
      </div>
    </form>
  );
}

const styles: Record<string, React.CSSProperties> = {
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
    padding: '20px',
    backgroundColor: '#2c2c2c',
    borderRadius: '8px'
  },
  field: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px'
  },
  input: {
    padding: '8px 12px',
    fontSize: '14px',
    border: '1px solid #444',
    borderRadius: '4px',
    backgroundColor: '#1a1a1a',
    color: '#fff'
  },
  buttons: {
    display: 'flex',
    gap: '8px',
    marginTop: '8px'
  },
  button: {
    padding: '8px 16px',
    backgroundColor: '#444',
    color: '#fff',
    borderRadius: '4px',
    border: 'none'
  },
  primaryButton: {
    padding: '8px 16px',
    backgroundColor: '#007bff',
    color: '#fff',
    borderRadius: '4px',
    border: 'none'
  },
  error: {
    padding: '8px',
    backgroundColor: '#f8d7da',
    color: '#721c24',
    borderRadius: '4px',
    fontSize: '14px'
  }
};
