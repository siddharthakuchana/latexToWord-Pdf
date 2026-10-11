const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ToolInfo {
  id: string;
  icon: string;
  name: string;
  tag: string;
  tagColor: string;
  desc: string;
}

export interface HealthStatus {
  status: string;
  tools: number;
  gtts_available: boolean;
  matplotlib_available: boolean;
  ocr_available: boolean;
  ocr_message: string;
}

export async function fetchHealth(): Promise<HealthStatus> {
  const res = await fetch(`${API_BASE}/api/health`);
  if (!res.ok) throw new Error('API unreachable');
  return res.json();
}

export async function fetchTools(): Promise<ToolInfo[]> {
  const res = await fetch(`${API_BASE}/api/tools`);
  if (!res.ok) throw new Error('Failed to load tools');
  return res.json();
}

// Generic file upload helper
export async function uploadFile(
  endpoint: string,
  file: File,
  extraFields?: Record<string, string | number | boolean>,
): Promise<Response> {
  const formData = new FormData();
  formData.append('file', file);
  if (extraFields) {
    for (const [k, v] of Object.entries(extraFields)) {
      formData.append(k, String(v));
    }
  }
  const res = await fetch(`${API_BASE}${endpoint}`, {
    method: 'POST',
    body: formData,
  });
  return res;
}

// Two-file upload (for diff)
export async function uploadTwoFiles(
  endpoint: string,
  fileA: File,
  fileB: File,
  extraFields?: Record<string, string | number | boolean>,
): Promise<Response> {
  const formData = new FormData();
  formData.append('file_a', fileA);
  formData.append('file_b', fileB);
  if (extraFields) {
    for (const [k, v] of Object.entries(extraFields)) {
      formData.append(k, String(v));
    }
  }
  const res = await fetch(`${API_BASE}${endpoint}`, {
    method: 'POST',
    body: formData,
  });
  return res;
}

export async function downloadFromResponse(res: Response, fallbackFilename: string): Promise<void> {
  const blob = await res.blob();
  const disposition = res.headers.get('Content-Disposition');
  let filename = fallbackFilename;
  if (disposition) {
    const match = disposition.match(/filename="?([^"]+)"?/);
    if (match) filename = match[1];
  }
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export async function fetchJSON<T>(endpoint: string, file: File, extraFields?: Record<string, string | number | boolean>): Promise<T> {
  const res = await uploadFile(endpoint, file, extraFields);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(err.detail || 'Request failed');
  }
  return res.json();
}

export async function uploadMultipleFiles(
  endpoint: string,
  files: File[],
  extraFields?: Record<string, string | number | boolean>
): Promise<Response> {
  const formData = new FormData();
  files.forEach((f) => formData.append('files', f));
  if (extraFields) {
    for (const [k, v] of Object.entries(extraFields)) {
      formData.append(k, String(v));
    }
  }
  return fetch(`${API_BASE}${endpoint}`, {
    method: 'POST',
    body: formData,
  });
}

export async function postForm(
  endpoint: string,
  fields: Record<string, string | number | boolean>
): Promise<Response> {
  const formData = new FormData();
  for (const [k, v] of Object.entries(fields)) {
    formData.append(k, String(v));
  }
  return fetch(`${API_BASE}${endpoint}`, {
    method: 'POST',
    body: formData,
  });
}

