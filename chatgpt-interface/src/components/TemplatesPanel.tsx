import React, { useState, useEffect } from 'react';
import { Template } from '../types';
import { saveTemplate, deleteTemplate, exportTemplates, importTemplates } from '../utils/storage';
import { generateId } from '../utils/crypto';

interface TemplatesPanelProps {
  userId: string;
  onInsertTemplate: (content: string) => void;
}

export const TemplatesPanel: React.FC<TemplatesPanelProps> = ({ userId, onInsertTemplate }) => {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<Template | null>(null);
  const [name, setName] = useState('');
  const [content, setContent] = useState('');
  const [showImport, setShowImport] = useState(false);
  const [importText, setImportText] = useState('');

  useEffect(() => {
    loadTemplates();
  }, [userId]);

  const loadTemplates = async () => {
    const { getTemplatesForUser } = await import('../utils/storage');
    const userTemplates = await getTemplatesForUser(userId);
    setTemplates(userTemplates);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const template: Template = {
      id: editingTemplate?.id || generateId(),
      userId,
      name,
      content,
      createdAt: editingTemplate?.createdAt || Date.now(),
      updatedAt: Date.now(),
    };

    await saveTemplate(template);
    await loadTemplates();
    resetForm();
  };

  const handleEdit = (template: Template) => {
    setEditingTemplate(template);
    setName(template.name);
    setContent(template.content);
    setShowForm(true);
  };

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this template?')) {
      await deleteTemplate(id);
      await loadTemplates();
    }
  };

  const resetForm = () => {
    setName('');
    setContent('');
    setEditingTemplate(null);
    setShowForm(false);
  };

  const handleExport = async () => {
    const json = await exportTemplates(userId);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `templates-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleImport = async () => {
    const count = await importTemplates(userId, importText);
    if (count > 0) {
      await loadTemplates();
      setImportText('');
      setShowImport(false);
      alert(`Successfully imported ${count} templates`);
    } else {
      alert('Failed to import templates. Please check the JSON format.');
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2 style={styles.title}>Templates</h2>
        <div style={styles.actions}>
          <button onClick={() => setShowImport(!showImport)} style={styles.iconButton}>
            📥
          </button>
          <button onClick={handleExport} style={styles.iconButton}>
            📤
          </button>
          <button onClick={() => setShowForm(true)} style={styles.addButton}>
            + New
          </button>
        </div>
      </div>

      {showImport && (
        <div style={styles.importBox}>
          <textarea
            value={importText}
            onChange={(e) => setImportText(e.target.value)}
            placeholder="Paste JSON here..."
            style={styles.textarea}
          />
          <div style={styles.importActions}>
            <button onClick={handleImport} style={styles.primaryButton}>Import</button>
            <button onClick={() => setShowImport(false)} style={styles.secondaryButton}>Cancel</button>
          </div>
        </div>
      )}

      {showForm && (
        <form onSubmit={handleSubmit} style={styles.form}>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Template name"
            style={styles.input}
            required
          />
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Template content (use {{placeholder}} for variables)"
            style={styles.textarea}
            rows={4}
            required
          />
          <div style={styles.formActions}>
            <button type="submit" style={styles.primaryButton}>
              {editingTemplate ? 'Update' : 'Create'}
            </button>
            <button type="button" onClick={resetForm} style={styles.secondaryButton}>
              Cancel
            </button>
          </div>
        </form>
      )}

      <div style={styles.list}>
        {templates.length === 0 ? (
          <p style={styles.empty}>No templates yet. Create one!</p>
        ) : (
          templates.map((template) => (
            <div key={template.id} style={styles.item}>
              <div style={styles.itemHeader}>
                <h3 style={styles.itemName}>{template.name}</h3>
                <div style={styles.itemActions}>
                  <button onClick={() => onInsertTemplate(template.content)} style={styles.insertButton}>
                    Insert
                  </button>
                  <button onClick={() => handleEdit(template)} style={styles.editButton}>
                    ✏️
                  </button>
                  <button onClick={() => handleDelete(template.id)} style={styles.deleteButton}>
                    🗑️
                  </button>
                </div>
              </div>
              <p style={styles.itemContent}>{template.content}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    background: 'white',
    borderRadius: '12px',
    padding: '20px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px',
  },
  title: {
    margin: 0,
    fontSize: '20px',
    color: '#333',
  },
  actions: {
    display: 'flex',
    gap: '8px',
  },
  iconButton: {
    background: '#f0f0f0',
    border: 'none',
    borderRadius: '6px',
    padding: '8px 12px',
    cursor: 'pointer',
    fontSize: '16px',
  },
  addButton: {
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    padding: '8px 16px',
    cursor: 'pointer',
    fontWeight: '600',
  },
  importBox: {
    marginBottom: '20px',
    padding: '15px',
    background: '#f9f9f9',
    borderRadius: '8px',
  },
  textarea: {
    width: '100%',
    padding: '12px',
    border: '2px solid #e0e0e0',
    borderRadius: '8px',
    fontSize: '14px',
    resize: 'vertical',
    fontFamily: 'inherit',
    boxSizing: 'border-box',
  },
  importActions: {
    display: 'flex',
    gap: '10px',
    marginTop: '10px',
  },
  form: {
    marginBottom: '20px',
    padding: '15px',
    background: '#f9f9f9',
    borderRadius: '8px',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  input: {
    padding: '12px',
    border: '2px solid #e0e0e0',
    borderRadius: '8px',
    fontSize: '14px',
  },
  formActions: {
    display: 'flex',
    gap: '10px',
  },
  primaryButton: {
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    padding: '10px 20px',
    cursor: 'pointer',
    fontWeight: '600',
  },
  secondaryButton: {
    background: '#f0f0f0',
    color: '#333',
    border: 'none',
    borderRadius: '6px',
    padding: '10px 20px',
    cursor: 'pointer',
  },
  list: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  empty: {
    textAlign: 'center',
    color: '#999',
    padding: '40px 0',
  },
  item: {
    background: '#f9f9f9',
    borderRadius: '8px',
    padding: '15px',
  },
  itemHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '8px',
  },
  itemName: {
    margin: 0,
    fontSize: '16px',
    color: '#333',
  },
  itemActions: {
    display: 'flex',
    gap: '8px',
  },
  insertButton: {
    background: '#4CAF50',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    padding: '6px 12px',
    cursor: 'pointer',
    fontSize: '13px',
  },
  editButton: {
    background: '#f0f0f0',
    border: 'none',
    borderRadius: '4px',
    padding: '6px 10px',
    cursor: 'pointer',
    fontSize: '14px',
  },
  deleteButton: {
    background: '#ffebee',
    border: 'none',
    borderRadius: '4px',
    padding: '6px 10px',
    cursor: 'pointer',
    fontSize: '14px',
  },
  itemContent: {
    margin: 0,
    color: '#666',
    fontSize: '14px',
    whiteSpace: 'pre-wrap',
    wordBreak: 'break-word',
  },
};
