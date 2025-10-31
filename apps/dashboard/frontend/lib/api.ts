// API Client
const API_BASE = '/api';

export async function fetchDashboardStats() {
  const res = await fetch(`${API_BASE}/dashboard/stats`);
  if (!res.ok) throw new Error('Failed to fetch stats');
  return res.json();
}

export async function fetchRuns() {
  const res = await fetch(`${API_BASE}/runs`);
  if (!res.ok) throw new Error('Failed to fetch runs');
  return res.json();
}

export async function fetchRun(id: string) {
  const res = await fetch(`${API_BASE}/runs/${id}`);
  if (!res.ok) throw new Error('Failed to fetch run');
  return res.json();
}

export async function fetchRunStatus(id: string) {
  const res = await fetch(`${API_BASE}/runs/${id}/status`);
  if (!res.ok) throw new Error('Failed to fetch run status');
  return res.json();
}

export async function fetchRunResults(id: string) {
  const res = await fetch(`${API_BASE}/runs/${id}/results`);
  if (!res.ok) throw new Error('Failed to fetch run results');
  return res.json();
}

import type { CreateRunRequest } from './types';

export async function createRun(data: CreateRunRequest) {
  const res = await fetch(`${API_BASE}/runs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to create run');
  return res.json();
}

export async function deleteRun(id: string) {
  const res = await fetch(`${API_BASE}/runs/${id}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to delete run');
  return res.json();
}

// File management API functions
export async function uploadFile(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  
  const res = await fetch(`${API_BASE}/files/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('Failed to upload file');
  return res.json();
}

export async function validateFilePath(path: string) {
  const res = await fetch(`${API_BASE}/files/validate?path=${encodeURIComponent(path)}`);
  if (!res.ok) throw new Error('Failed to validate file path');
  return res.json();
}

export async function browseFolder(path: string) {
  const res = await fetch(`${API_BASE}/files/browse?path=${encodeURIComponent(path)}`);
  if (!res.ok) throw new Error('Failed to browse folder');
  return res.json();
}

export async function fetchCollapseFeatures(id: string) {
  const res = await fetch(`${API_BASE}/runs/${id}/collapse-features`);
  if (!res.ok) throw new Error('Failed to fetch collapse features');
  return res.json();
}
