// WebSocket hook for Edit Agent chat
// Connects to ws://localhost:8000/ws/chat/:runId

import { useEffect, useRef, useState } from 'react';
import type { ChatMessage } from '../types';

const WS_BASE = import.meta.env.VITE_WS_BASE || 'ws://localhost:8000';

interface UseChatWebSocketOptions {
  runId: string;
  onMessage?: (message: ChatMessage) => void;
  enabled?: boolean;
}

interface WebSocketState {
  connected: boolean;
  error: Error | null;
  sending: boolean;
}

export function useChatWebSocket({
  runId,
  onMessage,
  enabled = true,
}: UseChatWebSocketOptions) {
  const [state, setState] = useState<WebSocketState>({
    connected: false,
    error: null,
    sending: false,
  });
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!enabled || !runId) return;

    console.log(`[ChatWS] Connecting to ws://localhost:8000/ws/chat/${runId}`);
    const ws = new WebSocket(`${WS_BASE}/ws/chat/${runId}`);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('[ChatWS] ✓ Connected to chat stream');
      setState((prev) => ({ ...prev, connected: true, error: null }));
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data) as ChatMessage;
        console.log('[ChatWS] Received message:', message.role, message.content?.substring(0, 50));
        if (onMessage) {
          onMessage(message);
        }
      } catch (err) {
        console.error('[ChatWS] Failed to parse message:', err);
      }
    };

    ws.onerror = (error) => {
      console.error('[ChatWS] ✗ WebSocket error:', error);
      setState((prev) => ({ ...prev, connected: false, error: new Error('WebSocket error') }));
    };

    ws.onclose = () => {
      console.log('[ChatWS] Connection closed');
      setState((prev) => ({ ...prev, connected: false }));
    };

    return () => {
      console.log('[ChatWS] Cleanup - closing connection');
      if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
        ws.close();
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [runId, enabled]); // Removed onMessage from dependencies - it should be stable via useCallback

  const sendMessage = (content: string) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      console.error('[ChatWS] Cannot send message: WebSocket not connected');
      return;
    }

    setState((prev) => ({ ...prev, sending: true }));

    try {
      const message = {
        role: 'user',
        content,
        time: new Date().toTimeString().slice(0, 8),
      };

      wsRef.current.send(JSON.stringify(message));
    } catch (err) {
      console.error('[ChatWS] Failed to send message:', err);
      setState((prev) => ({ ...prev, error: new Error('Failed to send message') }));
    } finally {
      setState((prev) => ({ ...prev, sending: false }));
    }
  };

  return {
    connected: state.connected,
    error: state.error,
    sending: state.sending,
    sendMessage,
    disconnect: () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    },
  };
}
