import { DEFAULT_HEADERS, readErrorMessage } from './apiClient';

export async function getDataset(page = 1, pageSize = 50) {
  try {
    const response = await fetch(`/api/v1/dataset?page=${page}&page_size=${pageSize}`, {
      method: 'GET',
      headers: DEFAULT_HEADERS,
    });

    if (!response.ok) {
      const message = await readErrorMessage(response);
      throw new Error(`Fetch dataset failed (${response.status}): ${message}`);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Unable to fetch dataset: ${error.message}`);
    }
    throw new Error('Unable to fetch dataset: Unknown error');
  }
}

export async function getBenchmarkData() {
  try {
    const response = await fetch('/api/v1/models/benchmark', {
      method: 'GET',
      headers: DEFAULT_HEADERS,
    });

    if (!response.ok) {
      const message = await readErrorMessage(response);
      throw new Error(`Fetch benchmarks failed (${response.status}): ${message}`);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Unable to fetch benchmarks: ${error.message}`);
    }
    throw new Error('Unable to fetch benchmarks: Unknown error');
  }
}

export async function getSimulatedScan() {
  try {
    const response = await fetch('/api/v1/hardware/simulate', {
      method: 'GET',
      headers: DEFAULT_HEADERS,
    });

    if (!response.ok) {
      const message = await readErrorMessage(response);
      throw new Error(`Fetch simulated scan failed (${response.status}): ${message}`);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Unable to simulate hardware scan: ${error.message}`);
    }
    throw new Error('Unable to simulate hardware scan: Unknown error');
  }
}
