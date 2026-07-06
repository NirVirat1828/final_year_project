export default function SkeletonLoader({ className = '', style = {} }) {
  return (
    <div 
      className={`animate-pulse rounded ${className}`} 
      style={{ 
        backgroundColor: 'rgba(255, 255, 255, 0.05)', 
        ...style 
      }} 
    />
  );
}
