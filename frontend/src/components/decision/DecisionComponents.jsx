import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import { Activity, ShieldAlert, ShieldCheck, Shield, Clock, TrendingUp, AlertTriangle, Info } from 'lucide-react';

// Color Mapping Helpers
const getRiskColor = (risk) => {
  switch (risk?.toLowerCase()) {
    case 'high': return '#E74C3C'; // Red
    case 'medium': return '#F1C40F'; // Yellow
    case 'low': return '#2ECC71'; // Green
    default: return 'var(--text-secondary)';
  }
};

const getRiskBg = (risk) => {
  switch (risk?.toLowerCase()) {
    case 'high': return 'rgba(231, 76, 60, 0.05)';
    case 'medium': return 'rgba(241, 196, 15, 0.05)';
    case 'low': return 'rgba(46, 204, 113, 0.05)';
    default: return 'var(--light-bg)';
  }
};

export function QualityScoreCard({ score }) {
  const data = [
    { name: 'Score', value: score },
    { name: 'Remaining', value: 100 - score }
  ];
  const color = score >= 80 ? '#2ECC71' : score >= 50 ? '#F1C40F' : '#E74C3C';
  
  return (
    <div className="glass-card flex flex-col items-center justify-center relative">
      <span className="text-muted w-full text-left" style={{ fontSize: '0.875rem', fontWeight: 600 }}>Quality Index</span>
      <div style={{ width: '100%', height: '120px', marginTop: '1rem' }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="100%"
              startAngle={180}
              endAngle={0}
              innerRadius={60}
              outerRadius={80}
              paddingAngle={0}
              dataKey="value"
              stroke="none"
              isAnimationActive={false}
            >
              <Cell key="cell-0" fill={color} />
              <Cell key="cell-1" fill="var(--border-color)" />
            </Pie>
          </PieChart>
        </ResponsiveContainer>
      </div>
      <div style={{ position: 'absolute', bottom: '1.5rem', textAlign: 'center' }}>
        <span className="text-h1" style={{ fontSize: '2rem' }}>{score}</span>
        <span className="text-muted" style={{ fontSize: '0.75rem', display: 'block', marginTop: '-4px' }}>/ 100</span>
      </div>
    </div>
  );
}

export function ConfidenceCard({ confidence }) {
  const levels = ['Low', 'Medium', 'High'];
  const currentIndex = levels.indexOf(confidence) !== -1 ? levels.indexOf(confidence) : 0;
  
  return (
    <div className="glass-card flex flex-col gap-4">
      <span className="text-muted" style={{ fontSize: '0.875rem', fontWeight: 600 }}>Confidence Rating</span>
      <div className="flex items-center gap-3">
        <Activity size={24} style={{ color: 'var(--text-primary)' }} />
        <span className="text-h2">{confidence}</span>
      </div>
      
      <div className="flex gap-1" style={{ width: '100%', height: '8px', borderRadius: '4px', overflow: 'hidden' }}>
        {levels.map((level, idx) => (
          <div 
            key={level}
            style={{ 
              flex: 1, 
              background: idx <= currentIndex 
                ? (currentIndex === 2 ? '#2ECC71' : currentIndex === 1 ? '#F1C40F' : '#E74C3C')
                : 'var(--border-color)',
              opacity: idx <= currentIndex ? 1 : 0.3
            }}
          />
        ))}
      </div>
      <span className="text-muted mt-auto" style={{ fontSize: '0.75rem' }}>AI predictive certainty level</span>
    </div>
  );
}

export function BusinessRiskCard({ risk }) {
  const color = getRiskColor(risk);
  const bg = getRiskBg(risk);
  
  return (
    <div className="glass-card flex flex-col gap-2 items-center justify-center" style={{ background: bg, border: `1px solid ${color}` }}>
      <span className="text-muted w-full text-left" style={{ fontSize: '0.875rem', fontWeight: 600 }}>Business Risk</span>
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', paddingTop: '0.5rem' }}>
        {risk === 'High' ? <ShieldAlert size={42} color={color} /> : risk === 'Medium' ? <Shield size={42} color={color} /> : <ShieldCheck size={42} color={color} />}
        <span style={{ fontSize: '1.25rem', fontWeight: 700, color: color, textTransform: 'uppercase', letterSpacing: '1px' }}>{risk} Risk</span>
      </div>
    </div>
  );
}

export function ShelfLifeCard({ estimatedShelfLife }) {
  return (
    <div className="glass-card flex flex-col gap-2">
      <span className="text-muted" style={{ fontSize: '0.875rem', fontWeight: 600 }}>Estimated Shelf Life</span>
      <div className="flex items-center gap-4 mt-2">
        <div style={{ padding: '0.75rem', background: 'rgba(255,140,66,0.1)', borderRadius: 'var(--radius-md)' }}>
          <Clock size={28} className="text-primary-orange" />
        </div>
        <span className="text-h1" style={{ fontSize: '1.75rem' }}>{estimatedShelfLife}</span>
      </div>
      <span className="text-muted mt-auto" style={{ fontSize: '0.75rem' }}>Projected viability based on current conditions</span>
    </div>
  );
}

export function RecommendationCard({ recommendation, warning, risk }) {
  const color = getRiskColor(risk);
  
  return (
    <div className="glass-card flex flex-col gap-4">
      <h3 className="text-h3 flex items-center gap-2" style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem' }}>
        <TrendingUp size={20} color={color} />
        Actionable Recommendation
      </h3>
      
      {warning && (
        <div style={{ padding: '1rem', background: 'rgba(231, 76, 60, 0.05)', borderLeft: '4px solid #E74C3C', borderRadius: 'var(--radius-sm)', display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
          <AlertTriangle size={20} color="#E74C3C" style={{ flexShrink: 0, marginTop: '2px' }} />
          <div>
            <h4 style={{ color: '#E74C3C', fontWeight: 600, fontSize: '0.875rem', marginBottom: '0.25rem' }}>Critical Warning</h4>
            <span style={{ fontSize: '0.875rem', color: 'var(--text-primary)' }}>{warning}</span>
          </div>
        </div>
      )}

      <div style={{ padding: '1rem', background: 'var(--light-bg)', borderRadius: 'var(--radius-sm)', display: 'flex', gap: '0.75rem', alignItems: 'flex-start', border: `1px solid var(--border-color)` }}>
        <Info size={20} color="var(--text-secondary)" style={{ flexShrink: 0, marginTop: '2px' }} />
        <p style={{ fontWeight: 500, fontSize: '0.9375rem', lineHeight: 1.6 }}>{recommendation}</p>
      </div>
    </div>
  );
}

export function ReasoningPanel({ reasoning }) {
  if (!reasoning || reasoning.length === 0) return null;
  
  return (
    <div className="glass-card flex flex-col gap-4">
      <h3 className="text-h3 flex items-center gap-2" style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem' }}>
        <Activity size={18} className="text-primary-orange" /> Execution Timeline
      </h3>
      <div style={{ display: 'flex', flexDirection: 'column', paddingLeft: '0.5rem', marginTop: '0.5rem' }}>
        {reasoning.map((reason, idx) => (
          <div key={idx} style={{ display: 'flex', gap: '1rem', position: 'relative', paddingBottom: idx === reasoning.length - 1 ? '0' : '1.5rem' }}>
            {/* Timeline Line */}
            {idx !== reasoning.length - 1 && (
              <div style={{ position: 'absolute', left: '7px', top: '16px', bottom: '0', width: '2px', background: 'var(--border-color)' }} />
            )}
            {/* Timeline Dot */}
            <div style={{ position: 'relative', zIndex: 1, width: '16px', height: '16px', borderRadius: '50%', background: 'var(--white)', border: '4px solid var(--primary-orange)', flexShrink: 0, marginTop: '4px' }} />
            
            {/* Content */}
            <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              {reason}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
