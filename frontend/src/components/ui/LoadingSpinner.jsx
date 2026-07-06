import { Loader } from 'lucide-react';

export default function LoadingSpinner({ size = 24, className = 'text-primary-orange' }) {
  return (
    <Loader size={size} className={`animate-spin ${className}`} />
  );
}
