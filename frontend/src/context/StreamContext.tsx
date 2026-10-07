import React, {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
  useCallback,
} from "react";
import type {
  Alert,
  DashboardData,
  RiskLevel,
  Transaction,
} from "../types";
import { api } from "../services/api";

export type ConnectionStatus = "connecting" | "connected" | "disconnected" | "error";

interface StreamContextType {
  status: ConnectionStatus;
  dashboard: DashboardData;
  transactions: Transaction[];
  alerts: Alert[];
  latestTransaction: Transaction | null;
  error: string | null;
  reconnect: () => void;
  pauseStream: () => void;
  resumeStream: () => void;
  isPaused: boolean;
}

const defaultDashboard: DashboardData = {
  current_time_step: 1,
  total_transactions: 0,
  active_alerts: 0,
  critical_alerts: 0,
  suspicious_communities: 6,
  risk_distribution: {
    LOW: 0,
    MEDIUM: 0,
    HIGH: 0,
    CRITICAL: 0,
  },
  risk_trend: [],
  recent_alerts: [],
};

const StreamContext = createContext<StreamContextType | undefined>(undefined);

const WS_URL =
  import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws/stream";

export const StreamProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [status, setStatus] = useState<ConnectionStatus>("connecting");
  const [dashboard, setDashboard] = useState<DashboardData>(defaultDashboard);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [latestTransaction, setLatestTransaction] = useState<Transaction | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPaused, setIsPaused] = useState<boolean>(false);

  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const isPausedRef = useRef<boolean>(false);
  isPausedRef.current = isPaused;

  // 1. Initial REST fetch for immediate dashboard state
  useEffect(() => {
    let isMounted = true;
    async function loadInitial() {
      try {
        const initialDash = await api.getDashboard();
        if (!isMounted) return;
        setDashboard((prev) => ({
          ...prev,
          ...initialDash,
        }));
        if (initialDash.recent_alerts && initialDash.recent_alerts.length > 0) {
          setAlerts(initialDash.recent_alerts);
        }
      } catch (err) {
        console.warn("Failed to load initial REST dashboard data, waiting for stream:", err);
      }
    }
    loadInitial();
    return () => {
      isMounted = false;
    };
  }, []);

  // 2. WebSocket Connection and Real-Time Pipeline
  const connectWebSocket = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.close();
      socketRef.current = null;
    }

    setStatus("connecting");
    setError(null);

    try {
      const ws = new WebSocket(WS_URL);
      socketRef.current = ws;

      ws.onopen = () => {
        setStatus("connected");
        setError(null);
      };

      ws.onmessage = (event) => {
        if (isPausedRef.current) return;

        try {
          const payload = JSON.parse(event.data);

          if (payload.type === "transaction" && payload.transaction) {
            const rawTx = payload.transaction;
            const analysis = payload.analysis || {
              risk_score: 0,
              risk_level: "LOW" as RiskLevel,
              evidence: [],
              recommended_action: "NO_ACTION",
            };

            const tx: Transaction = {
              id: String(rawTx.id || rawTx.txId),
              txId: String(rawTx.txId || rawTx.id),
              time_step: Number(rawTx.time_step),
              amount: 0,
              risk_score: Number(analysis.risk_score),
              risk_level: analysis.risk_level as RiskLevel,
              ml_score: Number(rawTx.ml_score),
              predicted_class: rawTx.predicted_class,
              threshold: Number(rawTx.threshold ?? 0.69),
              temporal_score: Number(rawTx.temporal_score),
              temporal_reasons: rawTx.temporal_reasons || [],
              evidence: analysis.evidence || [],
              recommended_action: analysis.recommended_action || "NO_ACTION",
            };

            setLatestTransaction(tx);

            setTransactions((prev) => [tx, ...prev.slice(0, 99)]);

            // Update live dashboard statistics authoritative from backend
            setDashboard((prev) => {
              const updatedDistribution = {
                ...prev.risk_distribution,
                [tx.risk_level]: (prev.risk_distribution[tx.risk_level] || 0) + 1,
              };

              // Update risk trend for current time_step
              const currentTrend = [...prev.risk_trend];
              const trendIdx = currentTrend.findIndex(
                (p) => p.time_step === tx.time_step
              );
              if (trendIdx >= 0) {
                // Moving average for the time step
                const existing = currentTrend[trendIdx];
                currentTrend[trendIdx] = {
                  time_step: tx.time_step,
                  risk: Math.round((existing.risk + tx.risk_score) / 2),
                };
              } else {
                currentTrend.push({
                  time_step: tx.time_step,
                  risk: Math.round(tx.risk_score),
                });
              }

              return {
                ...prev,
                current_time_step: tx.time_step,
                total_transactions: prev.total_transactions + 1,
                risk_distribution: updatedDistribution,
                risk_trend: currentTrend.slice(-20),
              };
            });
          } else if (payload.type === "alert" && payload.alert) {
            const newAlert: Alert = {
              id: payload.alert.id,
              transaction_id: String(payload.alert.transaction_id),
              risk_score: Number(payload.alert.risk_score),
              risk_level: payload.alert.risk_level as RiskLevel,
              reasons: payload.alert.reasons || [],
              recommended_action: payload.alert.recommended_action || "INVESTIGATE",
            };

            setAlerts((prev) => {
              if (prev.some((a) => a.id === newAlert.id)) return prev;
              return [newAlert, ...prev.slice(0, 49)];
            });

            setDashboard((prev) => {
              const updatedAlerts = [
                newAlert,
                ...prev.recent_alerts.filter((a) => a.id !== newAlert.id).slice(0, 9),
              ];
              const isCrit = newAlert.risk_level === "CRITICAL";
              return {
                ...prev,
                active_alerts: prev.active_alerts + 1,
                critical_alerts: isCrit ? prev.critical_alerts + 1 : prev.critical_alerts,
                recent_alerts: updatedAlerts,
              };
            });
          } else if (payload.type === "timestep_completed") {
            setDashboard((prev) => ({
              ...prev,
              current_time_step: payload.time_step + 1,
            }));
          }
        } catch (err) {
          console.error("Error parsing WebSocket message:", err);
        }
      };

      ws.onerror = (e) => {
        console.error("WebSocket error:", e);
        setStatus("error");
        setError("WebSocket connection failed. Ensure backend is running on :8000");
      };

      ws.onclose = () => {
        setStatus("disconnected");
        // Auto-reconnect after 3 seconds
        if (!reconnectTimeoutRef.current) {
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectTimeoutRef.current = null;
            connectWebSocket();
          }, 3000);
        }
      };
    } catch (err: any) {
      setStatus("error");
      setError(err?.message || "Failed to establish WebSocket connection");
    }
  }, []);

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [connectWebSocket]);

  const reconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    connectWebSocket();
  }, [connectWebSocket]);

  const pauseStream = useCallback(() => setIsPaused(true), []);
  const resumeStream = useCallback(() => setIsPaused(false), []);

  return (
    <StreamContext.Provider
      value={{
        status,
        dashboard,
        transactions,
        alerts,
        latestTransaction,
        error,
        reconnect,
        pauseStream,
        resumeStream,
        isPaused,
      }}
    >
      {children}
    </StreamContext.Provider>
  );
};

export const useStream = () => {
  const context = useContext(StreamContext);
  if (!context) {
    throw new Error("useStream must be used within a StreamProvider");
  }
  return context;
};
