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
              <span>Estimated Age</span>
              <strong>{resultsData?.logistics?.estimated_age_days ?? 'N/A'} days</strong>
            </div>

            <div className="metric-row">
              <span>Confidence Interval</span>
              <strong>{formatConfidenceInterval(resultsData?.logistics?.confidence_interval)}</strong>
            </div>
          </section>
        </div>
      </article>
    </section>
  )
}
