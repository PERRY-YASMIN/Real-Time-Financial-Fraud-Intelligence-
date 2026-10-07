import axios from "axios";
import type {
  Alert,
  DashboardData,
  NetworkData,
  Transaction,
  BackendTransactionPayload,
} from "../types";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});

export interface HealthResponse {
  status: string;
  nodes: number;
  edges: number;
}

export interface AlertsResponse {
  alerts: Alert[];
  count: number;
}

export const api = {
  async getHealth(): Promise<HealthResponse> {
    const res = await apiClient.get<HealthResponse>("/health");
    return res.data;
  },

  async getDashboard(): Promise<DashboardData> {
    const res = await apiClient.get<DashboardData>("/dashboard");
    return res.data;
  },

  async getAlerts(): Promise<AlertsResponse> {
    const res = await apiClient.get<AlertsResponse>("/alerts");
    return res.data;
  },

  async getAlert(alertId: string): Promise<Alert> {
    const res = await apiClient.get<Alert>(`/alerts/${alertId}`);
    return res.data;
  },

  async getTransaction(txId: string): Promise<Transaction> {
    const res = await apiClient.get<BackendTransactionPayload>(
      `/transactions/${txId}`
    );
    const data = res.data;
    const analysis = data.analysis || {
      risk_score: 0,
      risk_level: "LOW" as const,
      evidence: [],
      recommended_action: "NO_ACTION",
    };

    return {
      id: String(data.transaction_id || data.txId || txId),
      txId: String(data.txId || data.transaction_id || txId),
      time_step: data.time_step,
      amount: 0,
      risk_score: analysis.risk_score,
      risk_level: analysis.risk_level,
      ml_score: data.ml_score,
      predicted_class: data.predicted_class,
      threshold: data.threshold,
      temporal_score: data.temporal_score,
      temporal_reasons: data.temporal_reasons,
      evidence: analysis.evidence,
      recommended_action: analysis.recommended_action,
    };
  },

  async getNetwork(txId?: string, hops: number = 1): Promise<NetworkData> {
    const endpoint = txId ? `/network/${txId}?hops=${hops}` : "/network";
    const res = await apiClient.get<any>(endpoint);
    const data = res.data;

    const nodes = (data.nodes || []).map((n: any) => ({
      id: String(n.id),
      label: n.label || `TX ${n.id}`,
      risk_score: n.risk_score !== undefined ? n.risk_score : 25,
      type: n.type || "transaction",
    }));

    const edges = (data.edges || []).map((e: any, idx: number) => ({
      id: e.id || `edge-${idx}`,
      source: String(e.source),
      target: String(e.target),
      weight: e.weight || 2,
    }));

    return { nodes, edges };
  },
};
