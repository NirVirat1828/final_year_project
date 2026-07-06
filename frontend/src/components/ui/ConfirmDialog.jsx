import { AlertTriangle, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function ConfirmDialog({ 
  isOpen, 
  title = "Confirm Action", 
  message = "Are you sure you want to proceed?", 
  confirmText = "Confirm",
  cancelText = "Cancel",
  isDestructive = false,
  isLoading = false,
  onConfirm, 
  onCancel 
}) {
  if (!isOpen) return null;

  const btnColor = isDestructive ? '#ef4444' : 'var(--primary-orange)';

  return (
    <AnimatePresence>
      <motion.div 
        className="modal-backdrop" 
        style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 100, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
      >
        <motion.div 
          className="glass-card" 
          style={{ width: '400px', maxWidth: '90vw', borderTop: `4px solid ${btnColor}` }}
          initial={{ scale: 0.9, y: 20 }}
          animate={{ scale: 1, y: 0 }}
          exit={{ scale: 0.9, y: 20 }}
        >
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-h3 flex items-center gap-2" style={{ color: btnColor }}>
              {isDestructive && <AlertTriangle size={20} />} {title}
            </h3>
            <button onClick={onCancel} className="text-muted hover:text-white transition-colors" disabled={isLoading}>
              <X size={20} />
            </button>
          </div>
          
          <p className="text-muted mb-6">
            {message}
          </p>
          
          <div className="flex justify-end gap-3">
            <button 
              className="btn btn-outline" 
              onClick={onCancel}
              disabled={isLoading}
            >
              {cancelText}
            </button>
            <button 
              className="btn btn-primary" 
              style={{ backgroundColor: btnColor, borderColor: btnColor }}
              onClick={onConfirm}
              disabled={isLoading}
            >
              {isLoading ? 'Processing...' : confirmText}
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
