// CineAI — TypeScript type definitions

export interface Phase {
  id: string;
  title: string;
  subtitle: string;
  icon: string;
  color: string;
}

export type JobStatus = 'pending' | 'queued' | 'running' | 'complete' | 'error';

export interface PhaseState {
  status: JobStatus;
  progress: number;
  duration?: string;
  start?: string;
  end?: string;
  substeps?: string[];
  lines?: string[];
}

export interface LogEntry {
  t: string;
  lvl: 'info' | 'debug' | 'warn' | 'error' | 'ok';
  tag: string;
  msg: string;
}

export interface Scene {
  id: number;
  label: string;
  start: number;
  end: number;
  color: string;
}

export interface Version {
  id: string;
  label: string;
  note: string;
  time: string;
  author: string;
  active?: boolean;
  changes: string[];
}

export interface EditTarget {
  type: 'Audio' | 'Video Frame' | 'Script' | 'Pacing' | null;
  detail?: string;
}

export interface PlanStep {
  label: string;
  diff: string;
}

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
  time: string;
  thinking?: string;
  targets?: EditTarget[];
  plan?: PlanStep[];
  confidence?: number;
  eta?: string;
  applied?: boolean;
  resultVersion?: string;
  pendingApproval?: boolean;
}

export interface GenerateRequest {
  prompt: string;
  genre: string;
  tone: string;
  duration: string;
  aspect: string;
}

export interface GenerateResponse {
  run_id: string;
  status: string;
  message: string;
}

export interface JobStatusResponse {
  run_id: string;
  status: JobStatus;
  phases: Record<string, PhaseState>;
  metadata?: {
    prompt: string;
    genre: string;
    tone: string;
    duration: string;
    aspect: string;
    started_at: string;
  };
}
