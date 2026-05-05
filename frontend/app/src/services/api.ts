// CineAI API Service Layer
// Centralized API calls to backend

import type { GenerateRequest, GenerateResponse, JobStatusResponse } from '../types';

const API_BASE = import.meta.env.VITE_API_BASE || '';

/**
 * Generate a new video from a prompt
 * POST /api/generate
 */
export async function generateVideo(request: GenerateRequest): Promise<GenerateResponse> {
  const response = await fetch(`${API_BASE}/api/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Failed to generate video: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get job status and phase states
 * GET /api/runs/:runId/status
 */
export async function getJobStatus(runId: string): Promise<JobStatusResponse> {
  const response = await fetch(`${API_BASE}/api/runs/${runId}/status`);

  if (!response.ok) {
    throw new Error(`Failed to fetch job status: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get video output and metadata
 * GET /api/runs/:runId/output
 */
export async function getVideoOutput(runId: string): Promise<any> {
  const response = await fetch(`${API_BASE}/api/runs/${runId}/output`);

  if (!response.ok) {
    throw new Error(`Failed to fetch video output: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get version history for a run
 * GET /api/runs/:runId/versions
 */
export async function getVersionHistory(runId: string): Promise<any> {
  const response = await fetch(`${API_BASE}/api/runs/${runId}/versions`);

  if (!response.ok) {
    throw new Error(`Failed to fetch version history: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Re-run a specific phase
 * POST /api/runs/:runId/phases/:phaseId/rerun
 */
export async function rerunPhase(runId: string, phaseId: string): Promise<any> {
  const response = await fetch(`${API_BASE}/api/runs/${runId}/phases/${phaseId}/rerun`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!response.ok) {
    throw new Error(`Failed to re-run phase: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Send a chat message to the edit agent
 * POST /api/runs/:runId/chat
 */
export async function sendChatMessage(runId: string, message: string): Promise<any> {
  const response = await fetch(`${API_BASE}/api/runs/${runId}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    throw new Error(`Failed to send chat message: ${response.statusText}`);
  }

  return response.json();
}
