// WebSocket hook for live progress updates
// Connects to ws://localhost:8000/ws/progress/:runId

import { useEffect, useRef, useState } from 'react';
import type { LogEntry } from '../types';

const WS_BASE = import.meta.env.VITE_WS_BASE || 'ws://localhost:8000';

interface UseProgressWebSocketOptions {
  runId: string;
  onLog?: (log: LogEntry) => void;
  onPhaseUpdate?: (phaseId: string, status: any) => void;
  enabled?: boolean;
}

interface WebSocketState {
  connected: boolean;
  error: Error | null;
}

export function useProgressWebSocket({
  runId,
  onLog,
  onPhaseUpdate,
  enabled = true,
}: UseProgressWebSocketOptions) {
  const [state, setState] = useState<WebSocketState>({
    connected: false,
    error: null,
  });
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!enabled || !runId) return;

    const ws = new WebSocket(`${WS_BASE}/ws/progress/${runId}`);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('[WebSocket] Connected to progress stream');
      setState({ connected: true, error: null });
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        // Handle different message types
        if (data.type === 'log' && onLog) {
          onLog(data.payload as LogEntry);
        } else if (data.type === 'phase_update' && onPhaseUpdate) {
          onPhaseUpdate(data.phase_id, data.status);
        }
      } catch (err) {
        // Silently ignore parse errors
      }
    };

    ws.onerror = () => {
      // Silently handle WebSocket errors - UI will show demo mode
      setState({ connected: false, error: new Error('WebSocket error') });
    };

    ws.onclose = () => {
      // Silently handle WebSocket close - UI will show demo mode
      setState({ connected: false, error: null });
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
        ws.close();
      }
    };
  }, [runId, enabled, onLog, onPhaseUpdate]);

  return {
    connected: state.connected,
    error: state.error,
    disconnect: () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    },
  };
}
