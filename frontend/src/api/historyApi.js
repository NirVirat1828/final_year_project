import { DEFAULT_HEADERS, readErrorMessage } from './apiClient';

export async function getPredictionHistory(page = 1, pageSize = 50) {
  try {
    const response = await fetch(`/api/v1/history?page=${page}&page_size=${pageSize}`, {
      method: 'GET',
      headers: DEFAULT_HEADERS,
    });

    if (!response.ok) {
      const message = await readErrorMessage(response);
      throw new Error(`Fetch history failed (${response.status}): ${message}`);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Unable to fetch history: ${error.message}`);
    }
    throw new Error('Unable to fetch history: Unknown error');
  }
}

export async function getPredictionById(id) {
  try {
    const response = await fetch(`/api/v1/history/${id}`, {
      method: 'GET',
      headers: DEFAULT_HEADERS,
    });

    if (!response.ok) {
      const message = await readErrorMessage(response);
      throw new Error(`Fetch prediction failed (${response.status}): ${message}`);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Unable to fetch prediction: ${error.message}`);
    }
    throw new Error('Unable to fetch prediction: Unknown error');
  }
}

export async function deletePrediction(id) {
  try {
    const response = await fetch(`/api/v1/history/${id}`, {
      method: 'DELETE',
      headers: DEFAULT_HEADERS,
    });

    if (!response.ok) {
      const message = await readErrorMessage(response);
      throw new Error(`Delete prediction failed (${response.status}): ${message}`);
    }
    
    return true;
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Unable to delete prediction: ${error.message}`);
    }
    throw new Error('Unable to delete prediction: Unknown error');
  }
}

export async function getPredictionStats() {
  try {
    const response = await fetch('/api/v1/history/stats', {
      method: 'GET',
      headers: DEFAULT_HEADERS,
    });

    if (!response.ok) {
      const message = await readErrorMessage(response);
      throw new Error(`Fetch stats failed (${response.status}): ${message}`);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Unable to fetch prediction stats: ${error.message}`);
    }
    throw new Error('Unable to fetch prediction stats: Unknown error');
  }
}
