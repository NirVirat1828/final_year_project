import { datasetItems, keyPaths, projectFacts, trackCards, workflowStages } from './data/projectData'

function App() {
  return (
    <div className="app-shell">
      <main className="dashboard">
        <section className="hero">
          <div className="hero-copy card">
            <p className="eyebrow">Project frontend</p>
            <h1>Orange freshness detection system</h1>
            <p className="hero-text">
              This UI is a clean presentation layer for the actual project. It shows what the
              system does, how the data flows, and where the code and reports live.
            </p>

            <ul className="fact-list">
              {projectFacts.map((fact) => (
                <li key={fact}>{fact}</li>
              ))}
            </ul>

            <div className="hero-actions">
              <a className="primary-btn" href="#pipeline">
                See the pipeline
              </a>
              <a className="secondary-btn" href="#files">
                Open project map
              </a>
            </div>
          </div>

          
        </section>

        <section className="section" id="pipeline">
          <div className="section-heading">
            <p className="eyebrow">Pipeline</p>
            <h2>From sensor readings to project outputs</h2>
          </div>

          <div className="timeline">
            {workflowStages.map((stage, index) => (
              <article className="timeline-step card" key={stage.title}>
                <div className="step-index">0{index + 1}</div>
                <h3>{stage.title}</h3>
                <p>{stage.text}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="section">
          <div className="section-heading">
            <p className="eyebrow">Outputs</p>
            <h2>The project is built around three practical predictions</h2>
          </div>

          <div className="track-grid">
            {trackCards.map((track) => (
              <article className="track-card card" key={track.title}>
                <p className="track-label">{track.title}</p>
                <h3>{track.subtitle}</h3>
                <p>{track.detail}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="section split-grid" id="files">
          <article className="card dataset-card">
            <div className="section-heading compact">
              <p className="eyebrow">Dataset map</p>
              <h2>Where the inputs live</h2>
            </div>

            <div className="list-stack">
              {datasetItems.map((item) => (
                <div className="list-item" key={item.path}>
                  <code>{item.path}</code>
                  <p>{item.note}</p>
                </div>
              ))}
            </div>
          </article>

          <article className="card artifact-card">
            <div className="section-heading compact">
              <p className="eyebrow">Repository scaffold</p>
              <h2>Code and reports are separated cleanly</h2>
            </div>

            <div className="artifact-chips">
              {keyPaths.map((item) => (
                <span key={item}>{item}</span>
              ))}
            </div>
          </article>
        </section>

        
      </main>
    </div>
  )
}

export default App
