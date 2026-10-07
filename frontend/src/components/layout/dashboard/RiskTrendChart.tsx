import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import { mockDashboard } from "../../../mocks/data";
import { useStream } from "../../../context/StreamContext";
import type { RiskTrendPoint } from "../../../types";

interface RiskTrendChartProps {
  data?: RiskTrendPoint[];
}

export default function RiskTrendChart({ data: propData }: RiskTrendChartProps) {
  const { dashboard } = useStream();
  const data =
    propData ||
    (dashboard.risk_trend && dashboard.risk_trend.length > 0
      ? dashboard.risk_trend
      : mockDashboard.risk_trend);

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={data}
          margin={{
            top: 10,
            right: 10,
            left: -10,
            bottom: 0,
          }}
        >
          <CartesianGrid
            stroke="#1f2937"
            strokeDasharray="3 3"
          />

          <XAxis
            dataKey="time_step"
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
            domain={[0, 100]}
            tick={{
              fill: "#6b7280",
              fontSize: 11,
            }}
            axisLine={false}
            tickLine={false}
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

          <Line
            type="monotone"
            dataKey="risk"
            stroke="#60a5fa"
            strokeWidth={2}
            dot={false}
            activeDot={{
              r: 4,
              fill: "#60a5fa",
            }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}