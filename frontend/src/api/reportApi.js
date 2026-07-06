import { readErrorMessage } from './apiClient';

export async function downloadPredictionReport(id) {
  try {
    const response = await fetch(`/api/v1/history/${id}/report`, {
      method: 'GET',
    });

    if (!response.ok) {
      const message = await readErrorMessage(response);
      throw new Error(`Download report failed (${response.status}): ${message}`);
    }

    const blob = await response.blob();
    return URL.createObjectURL(blob);
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Unable to download report: ${error.message}`);
    }
    throw new Error('Unable to download report: Unknown error');
  }
}
