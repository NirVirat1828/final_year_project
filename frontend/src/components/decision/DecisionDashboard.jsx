import React from 'react';
import { 
  QualityScoreCard, 
  ConfidenceCard, 
  BusinessRiskCard, 
  ShelfLifeCard, 
  RecommendationCard, 
  ReasoningPanel 
} from './DecisionComponents';

export default function DecisionDashboard({ decisionData }) {
  if (!decisionData) return null;

  return (
    <section className="flex flex-col gap-4 mt-6 mb-6">
      <div className="section-heading mb-2" style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem' }}>
        <p className="eyebrow text-muted" style={{ textTransform: 'uppercase', fontSize: '0.75rem', fontWeight: 600 }}>Decision Engine Output</p>
        <h2 className="text-h2">Business Support Overview</h2>
      </div>
      
      <div className="grid-cols-4">
        <QualityScoreCard score={decisionData.quality_score} />
        <BusinessRiskCard risk={decisionData.business_risk} />
        <ConfidenceCard confidence={decisionData.confidence} />
        <ShelfLifeCard estimatedShelfLife={decisionData.estimated_shelf_life} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginTop: '1rem' }}>
        <RecommendationCard 
          recommendation={decisionData.recommendation} 
          warning={decisionData.warning} 
          risk={decisionData.business_risk} 
        />
        <ReasoningPanel reasoning={decisionData.reasoning} />
      </div>
    </section>
  );
}
