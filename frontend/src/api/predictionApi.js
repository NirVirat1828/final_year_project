import { DEFAULT_HEADERS, readErrorMessage } from './apiClient';

export async function analyzeBatch(payload) {
  try {
    const response = await fetch('/api/v1/analyze-batch', {
      method: 'POST',
      headers: DEFAULT_HEADERS,
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const message = await readErrorMessage(response);
      throw new Error(`Analyze batch failed (${response.status}): ${message}`);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Unable to analyze batch: ${error.message}`);
    }
    throw new Error('Unable to analyze batch: Unknown error');
  }
}

export async function analyzeCsvBatch(file, preprocessingStrategy = 'raw', storageTemperature = 4.0) {
  try {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('preprocessing_strategy', preprocessingStrategy);
    formData.append('storage_temperature_c', storageTemperature);

    const response = await fetch('/api/v1/analyze-csv', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const message = await readErrorMessage(response);
      throw new Error(`Analyze CSV batch failed (${response.status}): ${message}`);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Unable to analyze CSV batch: ${error.message}`);
    }
    throw new Error('Unable to analyze CSV batch: Unknown error');
  }
}
