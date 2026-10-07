export type RiskLevel = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export type EvidenceCategory = "ML" | "GRAPH" | "TEMPORAL";

export interface Evidence {
  category: EvidenceCategory;
  message: string;
}

export interface Alert {
  id: string;
  transaction_id: string;
  risk_score: number;
  risk_level: RiskLevel;
  reasons: Evidence[];
  recommended_action: string;
}

export interface Transaction {
  id: string;
  txId?: string;
  time_step: number;
  amount?: number;
  risk_score: number;
  risk_level: RiskLevel;
  ml_score?: number;
  predicted_class?: "ILLICIT" | "LICIT";
  threshold?: number;
  temporal_score?: number;
  temporal_reasons?: string[];
  graph_score?: number;
  evidence?: Evidence[];
  recommended_action?: string;
}

export interface BackendTransactionPayload {
  transaction_id?: string;
  txId?: string;
  id?: string;
  time_step: number;
  ml_score: number;
  predicted_class: "ILLICIT" | "LICIT";
  threshold: number;
  temporal_score: number;
  temporal_reasons: string[];
  risk_factors?: string[];
  analysis?: {
    risk_score: number;
    risk_level: RiskLevel;
    evidence: Evidence[];
    recommended_action: string;
  };
}

export interface NetworkNode {
  id: string;
  label: string;
  risk_score: number;
  type: string;
}

export interface NetworkEdge {
  id: string;
  source: string;
  target: string;
  weight: number;
}

export interface NetworkData {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
}

export interface RiskTrendPoint {
  time_step: number;
  risk: number;
}

export interface DashboardData {
  current_time_step: number;
  total_transactions: number;
  active_alerts: number;
  critical_alerts: number;
  suspicious_communities: number;

  risk_distribution: {
    LOW: number;
    MEDIUM: number;
    HIGH: number;
    CRITICAL: number;
  };

  risk_trend: RiskTrendPoint[];

  recent_alerts: Alert[];
}