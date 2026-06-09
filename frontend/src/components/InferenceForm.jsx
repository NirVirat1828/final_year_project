import { useState } from 'react'

const INITIAL_SENSOR_READINGS = Array.from({ length: 11 }, () => 0)

function generateMockSensorReadings() {
  return [21.21, 24.93, 1.87, 2315236.74, -0.82, 0.92, 53.77, -26.79, 9.8, -35.35, -23.0]
}

export default function InferenceForm({ onSubmit }) {
  const [batchId, setBatchId] = useState('BATCH-8821')
  const [preprocessingStrategy, setPreprocessingStrategy] = useState('raw')
  const [storageTemperatureC, setStorageTemperatureC] = useState(4)
  const [sensorReadings, setSensorReadings] = useState(INITIAL_SENSOR_READINGS)

  const handleSimulateSensorScan = () => {
    setSensorReadings(generateMockSensorReadings())
  }

  const handleSubmit = (event) => {
    event.preventDefault()

    const payload = {
      batch_id: batchId,
      sensor_readings: sensorReadings,
      preprocessing_strategy: preprocessingStrategy,
      storage_temperature_c: Number(storageTemperatureC),
    }

    if (typeof onSubmit === 'function') {
      onSubmit(payload)
    }
  }

  return (
    <section className="section">
      <div className="section-heading">
        <p className="eyebrow">Live inference</p>
        <h2>Prepare a batch for prediction</h2>
      </div>

      <form className="inference-form card" onSubmit={handleSubmit}>
        <div className="form-grid">
          <label className="field-group">
            <span>Batch ID</span>
            <input
              type="text"
              value={batchId}
              onChange={(event) => setBatchId(event.target.value)}
              placeholder="BATCH-8821"
            />
          </label>

          <label className="field-group">
            <span>Preprocessing strategy</span>
            <select
              value={preprocessingStrategy}
              onChange={(event) => setPreprocessingStrategy(event.target.value)}
            >
              <option value="raw">raw</option>
              <option value="advanced">advanced</option>
            </select>
          </label>
        </div>

        <label className="field-group slider-group">
          <span>Storage temperature: {Number(storageTemperatureC).toFixed(1)}°C</span>
          <input
            type="range"
            min="4"
            max="24"
            step="0.1"
            value={storageTemperatureC}
            onChange={(event) => setStorageTemperatureC(parseFloat(event.target.value))}
          />
          <div className="slider-labels">
            <span>4.0°C</span>
            <span>24.0°C</span>
          </div>
        </label>

        <div className="sensor-panel">
          <div className="sensor-panel-header">
            <div>
              <p className="panel-title">Sensor readings</p>
              <p className="panel-note">A mock scan generates the 11 input values required by the backend.</p>
            </div>

            <button type="button" className="secondary-btn simulate-btn" onClick={handleSimulateSensorScan}>
              Simulate Sensor Scan
            </button>
          </div>

          <div className="sensor-readings">
            {sensorReadings.map((reading, index) => (
              <div className="sensor-chip" key={`${index}-${reading}`}>
                <span>{String(index + 1).padStart(2, '0')}</span>
                <strong>{Number(reading).toFixed(2)}</strong>
              </div>
            ))}
          </div>
        </div>

        <div className="form-actions">
          <button type="submit" className="primary-btn submit-btn">
            Analyze Batch
          </button>
        </div>
      </form>
    </section>
  )
}
