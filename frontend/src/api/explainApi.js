import { DEFAULT_HEADERS, readErrorMessage } from './apiClient';

export async function explainPrediction(payload) {
  try {
    const response = await fetch('/api/v1/explain', {
      method: 'POST',
      headers: DEFAULT_HEADERS,
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const message = await readErrorMessage(response);
      throw new Error(`Explain prediction failed (${response.status}): ${message}`);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Unable to explain prediction: ${error.message}`);
    }
    throw new Error('Unable to explain prediction: Unknown error');
  }
}

export async function explainPredictionVisualize(payload, model = 'day', plotType = 'waterfall') {
  try {
    const response = await fetch(`/api/v1/explain/visualize?model=${model}&plot_type=${plotType}`, {
      method: 'POST',
      headers: DEFAULT_HEADERS,
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const message = await readErrorMessage(response);
      throw new Error(`Visualize explanation failed (${response.status}): ${message}`);
    }

    const blob = await response.blob();
    return URL.createObjectURL(blob);
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Unable to visualize explanation: ${error.message}`);
    }
    throw new Error('Unable to visualize explanation: Unknown error');
  }
}
