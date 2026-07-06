export const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
};

export async function readErrorMessage(response) {
  const contentType = response.headers.get('content-type') || '';

  if (contentType.includes('application/json')) {
    try {
      const errorBody = await response.json();
      return errorBody?.detail || errorBody?.message || JSON.stringify(errorBody);
    } catch {
      return `Request failed with status ${response.status}`;
    }
  }

  try {
    const text = await response.text();
    return text || `Request failed with status ${response.status}`;
  } catch {
    return `Request failed with status ${response.status}`;
  }
}
