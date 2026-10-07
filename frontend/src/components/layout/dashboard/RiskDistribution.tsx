import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

import { mockDashboard } from "../../../mocks/data";

const COLORS = {
  LOW: "#22c55e",
  MEDIUM: "#eab308",
  HIGH: "#f97316",
  CRITICAL: "#ef4444",
};

export default function RiskDistribution() {
  const distribution = mockDashboard.risk_distribution;

  const data = [
    {
      level: "LOW",
      count: distribution.LOW,
    },
    {
      level: "MEDIUM",
      count: distribution.MEDIUM,
    },
    {
      level: "HIGH",
      count: distribution.HIGH,
    },
    {
      level: "CRITICAL",
      count: distribution.CRITICAL,
    },
  ];

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          layout="vertical"
          margin={{
            top: 5,
            right: 10,
            left: 10,
            bottom: 5,
          }}
        >
          <CartesianGrid
            stroke="#1f2937"
            strokeDasharray="3 3"
            horizontal={false}
          />

          <XAxis
            type="number"
            tick={{
              fill: "#6b7280",
              fontSize: 11,
            }}
            axisLine={{
              stroke: "#374151",
            }}
            tickLine={false}
          />

          <YAxis
            type="category"
            dataKey="level"
            tick={{
              fill: "#9ca3af",
              fontSize: 11,
            }}
            axisLine={false}
            tickLine={false}
            width={65}
          />

          <Tooltip
            contentStyle={{
              backgroundColor: "#0f141b",
              border: "1px solid #374151",
              borderRadius: "6px",
              color: "#fff",
            }}
            labelStyle={{
              color: "#9ca3af",
            }}
          />

          <Bar
            dataKey="count"
            radius={[0, 4, 4, 0]}
          >
            {data.map((entry) => (
              <Cell
                key={entry.level}
                fill={COLORS[entry.level as keyof typeof COLORS]}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}