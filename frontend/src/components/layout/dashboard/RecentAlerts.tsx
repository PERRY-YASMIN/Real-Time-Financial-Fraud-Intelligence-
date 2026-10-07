import { AlertTriangle, ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";
import type { Alert } from "../../../types";
import { useStream } from "../../../context/StreamContext";

const riskStyles = {
  LOW: "text-green-400 bg-green-400/10 border-green-400/20",
  MEDIUM: "text-yellow-400 bg-yellow-400/10 border-yellow-400/20",
  HIGH: "text-orange-400 bg-orange-400/10 border-orange-400/20",
  CRITICAL: "text-red-400 bg-red-400/10 border-red-400/20",
};

interface RecentAlertsProps {
  alerts?: Alert[];
}

export default function RecentAlerts({ alerts: propAlerts }: RecentAlertsProps) {
  const { alerts: streamAlerts } = useStream();
  const alerts = propAlerts || (streamAlerts.length > 0 ? streamAlerts : []);

  return (
    <div className="overflow-hidden rounded-lg border border-gray-800 bg-[#0f141b]">
      
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-800 p-5">
        <div>
          <h3 className="text-sm font-medium text-white">
            Recent Alerts
          </h3>

          <p className="mt-1 text-xs text-gray-500">
            Suspicious transactions requiring analyst attention
          </p>
        </div>

        <Link to="/alerts" className="flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300">
          View all
          <ArrowRight size={14} />
        </Link>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left">

          <thead className="border-b border-gray-800 bg-[#0c1117]">
            <tr>
              <th className="px-5 py-3 text-xs font-medium uppercase tracking-wider text-gray-500">
                Transaction
              </th>

              <th className="px-5 py-3 text-xs font-medium uppercase tracking-wider text-gray-500">
                Score
              </th>

              <th className="px-5 py-3 text-xs font-medium uppercase tracking-wider text-gray-500">
                Risk
              </th>

              <th className="px-5 py-3 text-xs font-medium uppercase tracking-wider text-gray-500">
                Signals
              </th>

              <th className="px-5 py-3 text-xs font-medium uppercase tracking-wider text-gray-500">
                Action
              </th>
            </tr>
          </thead>

          <tbody className="divide-y divide-gray-800">
            {alerts.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-5 py-8 text-center text-xs text-gray-500">
                  Awaiting suspicious transaction alerts from real-time stream...
                </td>
              </tr>
            ) : (
              alerts.map((alert) => (
                <tr
                  key={alert.id}
                  className="transition-colors hover:bg-white/[0.02]"
                >

                {/* Transaction */}
                <td className="px-5 py-4">
                  <div className="flex items-center gap-2">

                    <AlertTriangle
                      size={15}
                      className="text-gray-500"
                    />

                    <span className="font-mono text-sm text-gray-300">
                      {alert.transaction_id}
                    </span>

                  </div>
                </td>

                {/* Score */}
                <td className="px-5 py-4">
                  <span className="font-mono text-sm font-medium text-white">
                    {alert.risk_score}
                  </span>
                </td>

                {/* Risk */}
                <td className="px-5 py-4">

                  <span
                    className={`rounded border px-2 py-1 text-xs font-medium ${
                      riskStyles[
                        alert.risk_level as keyof typeof riskStyles
                      ]
                    }`}
                  >
                    {alert.risk_level}
                  </span>

                </td>

                {/* Signals */}
                <td className="px-5 py-4">

                  <div className="flex flex-wrap gap-1.5">

                    {alert.reasons.map((reason) => (
                      <span
                        key={reason.category}
                        className="rounded border border-gray-700 bg-gray-800/40 px-2 py-1 text-[10px] font-medium text-gray-400"
                        title={reason.message}
                      >
                        {reason.category}
                      </span>
                    ))}

                  </div>

                </td>

                {/* Action */}
                <td className="px-5 py-4">

                  <button
                    className={`rounded border px-3 py-1.5 text-xs font-medium transition-colors ${
                      alert.recommended_action === "INVESTIGATE"
                        ? "border-blue-500/40 text-blue-400 hover:bg-blue-500/10"
                        : "border-gray-700 text-gray-300 hover:border-blue-500 hover:text-blue-400"
                    }`}
                  >
                    {alert.recommended_action}
                  </button>

                </td>

              </tr>
            )))}

          </tbody>
        </table>
      </div>
    </div>
  );
}