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
