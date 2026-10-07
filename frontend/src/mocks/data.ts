import type {
  Alert,
  DashboardData,
  NetworkData,
  Transaction,
} from "../types";

export const mockAlerts: Alert[] = [
  {
    id: "alert-001",
    transaction_id: "tx-1928",
    risk_score: 94,
    risk_level: "CRITICAL",
    reasons: [
      {
        category: "ML",
        message: "Elevated probability of illicit activity",
      },
      {
        category: "GRAPH",
        message: "Connected to a high-risk community",
      },
      {
        category: "TEMPORAL",
        message: "Transaction velocity increased significantly",
      },
    ],
    recommended_action: "INVESTIGATE",
  },

  {
    id: "alert-002",
    transaction_id: "tx-1930",
    risk_score: 82,
    risk_level: "HIGH",
    reasons: [
      {
        category: "GRAPH",
        message: "Entity has unusually high network connectivity",
      },
    ],
    recommended_action: "INVESTIGATE",
  },

  {
    id: "alert-003",
    transaction_id: "tx-1937",
    risk_score: 67,
    risk_level: "HIGH",
    reasons: [
      {
        category: "TEMPORAL",
        message:
          "Activity increased sharply within the recent time window",
      },
    ],
    recommended_action: "REVIEW",
  },
];

export const mockTransactions: Transaction[] = [
  {
    id: "tx-1928",
    time_step: 17,
    amount: 12.4,
    risk_score: 94,
    risk_level: "CRITICAL",
  },

  {
    id: "tx-1929",
    time_step: 17,
    amount: 2.1,
    risk_score: 21,
    risk_level: "LOW",
  },

  {
    id: "tx-1930",
    time_step: 17,
    amount: 8.7,
    risk_score: 82,
    risk_level: "HIGH",
  },
];

export const mockDashboard: DashboardData = {
  current_time_step: 17,

  total_transactions: 31204,

  active_alerts: 184,

  critical_alerts: 27,

  suspicious_communities: 6,

  risk_distribution: {
    LOW: 18500,
    MEDIUM: 8200,
    HIGH: 3200,
    CRITICAL: 1304,
  },

  risk_trend: [
    { time_step: 1, risk: 21 },
    { time_step: 2, risk: 28 },
    { time_step: 3, risk: 24 },
    { time_step: 4, risk: 35 },
    { time_step: 5, risk: 31 },
    { time_step: 6, risk: 47 },
    { time_step: 7, risk: 44 },
    { time_step: 8, risk: 53 },
    { time_step: 9, risk: 49 },
    { time_step: 10, risk: 61 },
    { time_step: 11, risk: 58 },
    { time_step: 12, risk: 65 },
    { time_step: 13, risk: 62 },
    { time_step: 14, risk: 71 },
    { time_step: 15, risk: 68 },
    { time_step: 16, risk: 76 },
    { time_step: 17, risk: 82 },
  ],

  recent_alerts: mockAlerts,
};

export const mockNetwork: NetworkData = {
  nodes: [
    {
      id: "A81",
      label: "Wallet A81",
      risk_score: 94,
      type: "wallet",
    },

    {
      id: "B72",
      label: "Wallet B72",
      risk_score: 81,
      type: "wallet",
    },

    {
      id: "C19",
      label: "Wallet C19",
      risk_score: 43,
      type: "wallet",
    },

    {
      id: "D44",
      label: "Wallet D44",
      risk_score: 76,
      type: "wallet",
    },

    {
      id: "E32",
      label: "Wallet E32",
      risk_score: 18,
      type: "wallet",
    },
  ],

  edges: [
    {
      id: "edge-1",
      source: "A81",
      target: "B72",
      weight: 4,
    },

    {
      id: "edge-2",
      source: "A81",
      target: "C19",
      weight: 2,
    },

    {
      id: "edge-3",
      source: "B72",
      target: "D44",
      weight: 3,
    },

    {
      id: "edge-4",
      source: "C19",
      target: "E32",
      weight: 1,
    },
  ],
};