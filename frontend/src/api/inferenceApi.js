const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
}

async function readErrorMessage(response) {
  const contentType = response.headers.get('content-type') || ''

  if (contentType.includes('application/json')) {
    try {
      const errorBody = await response.json()
      return errorBody?.detail || errorBody?.message || JSON.stringify(errorBody)
    } catch {
      return `Request failed with status ${response.status}`
    }
  }

  try {
    const text = await response.text()
    return text || `Request failed with status ${response.status}`
  } catch {
    return `Request failed with status ${response.status}`
  }
}

export async function checkHealth() {
  try {
    const response = await fetch('/api/v1/health', {
      method: 'GET',
      headers: DEFAULT_HEADERS,
    })

    if (!response.ok) {
      const message = await readErrorMessage(response)
      throw new Error(`Health check failed (${response.status}): ${message}`)
    }

    return await response.json()
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Unable to check backend health: ${error.message}`)
    }

    throw new Error('Unable to check backend health: Unknown error')
  }
}

export async function analyzeBatch(payload) {
  try {
    const response = await fetch('/api/v1/analyze-batch', {
      method: 'POST',
      headers: DEFAULT_HEADERS,
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      const message = await readErrorMessage(response)
      throw new Error(`Analyze batch failed (${response.status}): ${message}`)
    }

    return await response.json()
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Unable to analyze batch: ${error.message}`)
    }

    throw new Error('Unable to analyze batch: Unknown error')
  }
}

export async function analyzeCsvBatch(file, preprocessingStrategy = 'raw', storageTemperature = 4.0) {
  try {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('preprocessing_strategy', preprocessingStrategy)
    formData.append('storage_temperature_c', storageTemperature)

    const response = await fetch('/api/v1/analyze-csv', {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      const message = await readErrorMessage(response)
      throw new Error(`Analyze CSV batch failed (${response.status}): ${message}`)
    }

    return await response.json()
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Unable to analyze CSV batch: ${error.message}`)
    }

    throw new Error('Unable to analyze CSV batch: Unknown error')
  }
}

export async function explainPrediction(payload) {
  try {
    const response = await fetch('/api/v1/explain', {
      method: 'POST',
      headers: DEFAULT_HEADERS,
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      const message = await readErrorMessage(response)
      throw new Error(`Explain prediction failed (${response.status}): ${message}`)
    }

    return await response.json()
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Unable to explain prediction: ${error.message}`)
    }

    throw new Error('Unable to explain prediction: Unknown error')
  }
}

export async function explainPredictionVisualize(payload, model = 'day', plotType = 'waterfall') {
  try {
    const response = await fetch(`/api/v1/explain/visualize?model=${model}&plot_type=${plotType}`, {
      method: 'POST',
      headers: DEFAULT_HEADERS,
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      const message = await readErrorMessage(response)
      throw new Error(`Visualize explanation failed (${response.status}): ${message}`)
    }

    const blob = await response.blob()
    return URL.createObjectURL(blob)
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Unable to visualize explanation: ${error.message}`)
    }

    throw new Error('Unable to visualize explanation: Unknown error')
  }
}


