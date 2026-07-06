import { DEFAULT_HEADERS, readErrorMessage } from './apiClient';

export async function checkHealth() {
  try {
    const response = await fetch('/api/v1/health', {
      method: 'GET',
      headers: DEFAULT_HEADERS,
    });

    if (!response.ok) {
      const message = await readErrorMessage(response);
      throw new Error(`Health check failed (${response.status}): ${message}`);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Unable to check backend health: ${error.message}`);
    }
    throw new Error('Unable to check backend health: Unknown error');
  }
}
