function getGradeClass(freshnessGrade) {
  switch (freshnessGrade) {
    case 'A':
      return 'grade-badge grade-a'
    case 'B':
      return 'grade-badge grade-b'
    case 'C':
      return 'grade-badge grade-c'
    case 'D':
      return 'grade-badge grade-d'
    default:
      return 'grade-badge'
  }
}

function shouldRenderWarning(temperatureWarning) {
  if (temperatureWarning === true) {
    return true
  }

  if (typeof temperatureWarning === 'string') {
    const normalized = temperatureWarning.trim().toLowerCase()
    return normalized === 'true' || normalized === '1' || normalized === 'yes'
  }

  return false
}

function formatConfidenceInterval(confidenceInterval) {
  if (!confidenceInterval) {
    return 'N/A'
  }

  if (typeof confidenceInterval === 'string') {
    return confidenceInterval
  }

  const lower = confidenceInterval.lower_bound ?? confidenceInterval.lower ?? confidenceInterval.min
  const upper = confidenceInterval.upper_bound ?? confidenceInterval.upper ?? confidenceInterval.max

  if (lower == null || upper == null) {
    return 'N/A'
  }

  return `${Number(lower).toFixed(2)} - ${Number(upper).toFixed(2)} days`
}

function formatConfidenceScore(confidenceScorePercent) {
  if (confidenceScorePercent == null) {
    return 'N/A'
  }

  return `${Number(confidenceScorePercent).toFixed(0)}%`
}

export default function ResultsDashboard({ resultsData }) {
  if (!resultsData) {
    return null
  }

  const freshnessGrade = resultsData?.results?.freshness_grade
  const temperatureWarning = resultsData?.logistics?.temperature_warning
  const showWarning = shouldRenderWarning(temperatureWarning)

  return (
    <section className="section">
      <div className="section-heading">
        <p className="eyebrow">Prediction results</p>
        <h2>Shelf Life Assessment Card</h2>
      </div>

      <article className="results-card card">
        {showWarning ? (
          <div className="warning-banner" role="alert">
            Adjust cold storage immediately. The current storage conditions may accelerate spoilage.
          </div>
        ) : null}

        <div className="results-grid">
          <section className="results-section">
            <p className="section-kicker">Quality Metrics</p>

            <div className="metric-row">
              <span>Freshness Grade</span>
              <strong className={getGradeClass(freshnessGrade)}>{freshnessGrade || 'N/A'}</strong>
            </div>

            <div className="metric-row">
              <span>Grade Description</span>
              <strong>{resultsData?.results?.grade_description || 'N/A'}</strong>
            </div>

            <div className="metric-row">
              <span>Folic Acid</span>
              <strong>{resultsData?.results?.folic_acid_uM ?? 'N/A'} µM</strong>
            </div>

            <div className="metric-row">
              <span>Nutritional Status</span>
              <strong>{resultsData?.results?.nutritional_status || 'N/A'}</strong>
            </div>
          </section>

          <section className="results-section logistics-section">
            <p className="section-kicker">Logistics Action Block</p>

            <div className="metric-row">
              <span>Remaining Shelf Life</span>
              <strong>{resultsData?.logistics?.remaining_shelf_life_days ?? 'N/A'} days</strong>
            </div>

            <div className="metric-row">
              <span>Confidence Score</span>
              <strong>{formatConfidenceScore(resultsData?.logistics?.confidence_score_percent)}</strong>
            </div>

            <div className="metric-row">
              <span>Estimated Age</span>
              <strong>{resultsData?.logistics?.estimated_age_days ?? 'N/A'} days</strong>
            </div>

            <div className="metric-row">
              <span>Confidence Interval</span>
              <strong>{formatConfidenceInterval(resultsData?.logistics?.confidence_interval)}</strong>
            </div>
          </section>
        </div>

        <section className="diagnostics-section" aria-labelledby="system-diagnostics-title">
          <div className="section-heading compact diagnostics-heading">
            <p className="section-kicker diagnostics-kicker">System Diagnostics</p>
            <h3 id="system-diagnostics-title">Engineering review panel</h3>
          </div>

          <div className="diagnostics-alert" role="alert">
            <strong className="diagnostics-alert-title">
              ⚠️ Engineering Note: Folic Acid Prediction Anomaly
            </strong>
            <p>
              The Folic Acid random forest model achieved an R² score of 0.9997. While
              mathematically perfect, in biological electrochemical datasets, this indicates
              potential sensor overfitting or data leakage. Independent HPLC lab validation is
              strictly required before commercial deployment.
            </p>
          </div>
        </section>

        {resultsData?.agreement_analysis && (
          <section className="diagnostics-section" style={{ borderTop: '1px solid var(--border-color)', paddingTop: '1.5rem', marginTop: '1.5rem' }} aria-labelledby="agreement-diagnostics-title">
            <div className="section-heading compact diagnostics-heading">
              <p className="section-kicker diagnostics-kicker">Reliability Diagnostics</p>
              <h3 id="agreement-diagnostics-title">Model Agreement consensus</h3>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem', marginTop: '0.75rem' }}>
              {/* Consensus Score Card */}
              <div className="glass-card" style={{ padding: '1.25rem', backgroundColor: 'var(--light-bg)', borderRadius: 'var(--radius-md)', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <h4 style={{ margin: 0, fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Consensus Reliability</h4>
                <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
                  <div style={{ display: 'flex', flexDirection: 'column' }}>
                    <span className="text-muted" style={{ fontSize: '0.75rem', fontWeight: 500 }}>Consensus Class</span>
                    <strong style={{ fontSize: '1.75rem', color: 'var(--text-primary)', lineHeight: 1.2, marginTop: '0.125rem' }}>
                      Class {resultsData.agreement_analysis.consensus_prediction}
                    </strong>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column' }}>
                    <span className="text-muted" style={{ fontSize: '0.75rem', fontWeight: 500 }}>Agreement Score</span>
                    <strong style={{ fontSize: '1.75rem', color: 'var(--primary-orange)', lineHeight: 1.2, marginTop: '0.125rem' }}>
                      {resultsData.agreement_analysis.agreement_percentage}%
                    </strong>
                  </div>
                </div>
                <div>
                  <span className="text-muted" style={{ fontSize: '0.75rem', display: 'block', marginBottom: '0.25rem', fontWeight: 500 }}>Agreement Level</span>
                  <span 
                    className="status-badge" 
                    style={{ 
                      display: 'inline-block',
                      padding: '0.25rem 0.75rem', 
                      borderRadius: 'var(--radius-sm)', 
                      fontSize: '0.8125rem', 
                      fontWeight: 600,
                      backgroundColor: 
                        resultsData.agreement_analysis.agreement_level === 'Very Strong' ? 'rgba(46, 204, 113, 0.15)' :
                        resultsData.agreement_analysis.agreement_level === 'Strong' ? 'rgba(52, 152, 219, 0.15)' :
                        resultsData.agreement_analysis.agreement_level === 'Moderate' ? 'rgba(245, 158, 11, 0.15)' :
                        'rgba(239, 68, 68, 0.15)',
                      color: 
                        resultsData.agreement_analysis.agreement_level === 'Very Strong' ? 'var(--success-green)' :
                        resultsData.agreement_analysis.agreement_level === 'Strong' ? '#3498DB' :
                        resultsData.agreement_analysis.agreement_level === 'Moderate' ? 'var(--primary-orange)' :
                        '#ef4444'
                    }}
                  >
                    {resultsData.agreement_analysis.agreement_level}
                  </span>
                </div>
              </div>

              {/* Individual Models Panel */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                <h4 style={{ margin: 0, fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Model Decision Panel</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '180px', overflowY: 'auto', paddingRight: '4px' }}>
                  {resultsData.agreement_analysis.model_predictions.map((pred, i) => (
                    <div 
                      key={i} 
                      style={{ 
                        display: 'flex', 
                        justifyContent: 'space-between', 
                        alignItems: 'center', 
                        padding: '0.625rem 0.875rem', 
                        backgroundColor: 'var(--white)', 
                        border: '1px solid var(--border-color)', 
                        borderRadius: 'var(--radius-sm)',
                        fontSize: '0.8125rem',
                        transition: 'all 0.15s ease'
                      }}
                    >
                      <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{pred.model_name}</span>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <span style={{ color: 'var(--text-secondary)', fontSize: '0.75rem' }}>
                          Pred: <strong style={{ color: 'var(--text-primary)', fontSize: '0.8125rem' }}>{pred.predicted_class}</strong>
                        </span>
                        <span 
                          style={{ 
                            padding: '0.125rem 0.375rem', 
                            borderRadius: '4px', 
                            fontSize: '0.75rem', 
                            fontWeight: 600,
                            backgroundColor: pred.inference_status === 'success' ? 'rgba(46, 204, 113, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                            color: pred.inference_status === 'success' ? 'var(--success-green)' : '#ef4444'
                          }}
                        >
                          {(pred.confidence_score * 100).toFixed(0)}% Conf
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </section>
        )}
      </article>
    </section>
  )
}
