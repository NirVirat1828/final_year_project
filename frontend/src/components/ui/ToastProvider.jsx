import { createContext, useContext, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, AlertCircle, Info, X } from 'lucide-react';

const ToastContext = createContext(null);

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((message, type = 'info', duration = 3000) => {
    const id = Date.now().toString();
    setToasts(prev => [...prev, { id, message, type }]);
    
    if (duration > 0) {
      setTimeout(() => {
        removeToast(id);
      }, duration);
    }
  }, []);

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ addToast, removeToast }}>
      {children}
      <div style={{ position: 'fixed', bottom: '2rem', right: '2rem', zIndex: 9999, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        <AnimatePresence>
          {toasts.map(toast => (
            <ToastItem key={toast.id} toast={toast} onDismiss={() => removeToast(toast.id)} />
          ))}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
}

function ToastItem({ toast, onDismiss }) {
  const icons = {
    success: <CheckCircle size={18} className="text-success-green" />,
    error: <AlertCircle size={18} style={{ color: '#ef4444' }} />,
    info: <Info size={18} className="text-primary-orange" />
  };

  const borders = {
    success: '1px solid rgba(16, 185, 129, 0.2)',
    error: '1px solid rgba(239, 68, 68, 0.2)',
    info: '1px solid rgba(255, 140, 66, 0.2)'
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 50, scale: 0.9 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9, transition: { duration: 0.2 } }}
      style={{ 
        display: 'flex', 
        alignItems: 'flex-start', 
        gap: '0.75rem',
        background: 'rgba(15, 23, 42, 0.95)',
        backdropFilter: 'blur(10px)',
        padding: '1rem',
        borderRadius: 'var(--radius-md)',
        border: borders[toast.type] || borders.info,
        boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.5)',
        minWidth: '250px',
        maxWidth: '350px'
      }}
    >
      <div style={{ marginTop: '2px' }}>
        {icons[toast.type] || icons.info}
      </div>
      <p style={{ flex: 1, margin: 0, fontSize: '0.875rem', color: 'var(--text-primary)', lineHeight: 1.4 }}>
        {toast.message}
      </p>
      <button 
        onClick={onDismiss}
        style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: '2px' }}
      >
        <X size={14} />
      </button>
    </motion.div>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}
