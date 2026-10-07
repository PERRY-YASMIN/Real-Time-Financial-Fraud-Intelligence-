import { Activity, Play, Pause } from "lucide-react";
import { useStream } from "../context/StreamContext";

const riskStyles = {
  LOW: "text-green-400 bg-green-400/10 border-green-400/20",
  MEDIUM: "text-yellow-400 bg-yellow-400/10 border-yellow-400/20",
  HIGH: "text-orange-400 bg-orange-400/10 border-orange-400/20",
  CRITICAL: "text-red-400 bg-red-400/10 border-red-400/20",
};

export default function LiveMonitor() {
  const {
    transactions,
    latestTransaction,
    status,
    isPaused,
    pauseStream,
    resumeStream,
    dashboard,
  } = useStream();

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-white">
            Live Stream Monitor
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Real-time transaction ingestion with zero-latency Person 1 ML inference, Option B temporal intelligence, and Person 2 risk fusion
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={isPaused ? resumeStream : pauseStream}
            className={`flex items-center gap-2 rounded-lg border px-3 py-2 text-xs font-medium transition-colors ${
              isPaused
                ? "border-green-500/30 bg-green-500/10 text-green-400 hover:bg-green-500/20"
                : "border-yellow-500/30 bg-yellow-500/10 text-yellow-400 hover:bg-yellow-500/20"
            }`}
          >
            {isPaused ? (
              <>
                <Play size={14} /> Resume Stream
              </>
            ) : (
              <>
                <Pause size={14} /> Pause Stream
              </>
            )}
          </button>
        </div>
      </div>

      {/* Real-time Telemetry Cards */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        {/* Total Processed */}
        <div className="rounded-lg border border-gray-800 bg-[#0f141b] p-4">
          <p className="text-xs font-medium uppercase text-gray-500">Processed Transactions</p>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold text-white">
              {dashboard.total_transactions.toLocaleString()}
            </span>
            <span className="text-xs text-blue-400 font-mono">Step {dashboard.current_time_step}</span>
          </div>
          <p className="mt-1 text-[11px] text-gray-500">Continuous replay clock</p>
        </div>

        {/* Latest Person 1 ML Inference */}
        <div className="rounded-lg border border-gray-800 bg-[#0f141b] p-4">
          <div className="flex items-center justify-between">
            <p className="text-xs font-medium uppercase text-gray-500">Person 1 ML Score</p>
            <span className="rounded bg-blue-500/10 px-1.5 py-0.5 text-[10px] font-mono text-blue-400">
              XGBoost (Thr: 0.69)
            </span>
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold font-mono text-white">
              {latestTransaction?.ml_score !== undefined
                ? latestTransaction.ml_score.toFixed(4)
                : "—"}
            </span>
            <span
              className={`rounded border px-2 py-0.5 text-xs font-medium ${
                latestTransaction?.predicted_class === "ILLICIT"
                  ? "border-red-500/30 bg-red-500/10 text-red-400"
                  : "border-green-500/30 bg-green-500/10 text-green-400"
              }`}
            >
              {latestTransaction?.predicted_class || "STANDBY"}
            </span>
          </div>
          <p className="mt-1 text-[11px] text-gray-500">182 frozen feature evaluation</p>
        </div>

        {/* Latest Person 1 Temporal Velocity */}
        <div className="rounded-lg border border-gray-800 bg-[#0f141b] p-4">
          <div className="flex items-center justify-between">
            <p className="text-xs font-medium uppercase text-gray-500">Temporal Context</p>
            <span className="rounded bg-purple-500/10 px-1.5 py-0.5 text-[10px] font-mono text-purple-400">
              Option B
            </span>
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold font-mono text-white">
              {latestTransaction?.temporal_score !== undefined
                ? latestTransaction.temporal_score.toFixed(4)
                : "—"}
            </span>
            <span className="text-xs text-purple-400">Network Velocity</span>
          </div>
          <p className="mt-1 text-[11px] text-gray-500">Network-level rolling context signal</p>
        </div>

        {/* Latest Person 2 Fused Risk */}
        <div className="rounded-lg border border-gray-800 bg-[#0f141b] p-4">
          <p className="text-xs font-medium uppercase text-gray-500">Person 2 Fused Risk</p>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold font-mono text-white">
              {latestTransaction?.risk_score !== undefined
                ? `${latestTransaction.risk_score.toFixed(1)}`
                : "—"}
            </span>
            {latestTransaction && (
              <span
                className={`rounded border px-2 py-0.5 text-xs font-medium ${
                  riskStyles[latestTransaction.risk_level]
                }`}
              >
                {latestTransaction.risk_level}
              </span>
            )}
          </div>
          <p className="mt-1 text-[11px] text-gray-500">Multi-signal aggregation: 50% ML + 30% Graph + 20% Temporal</p>
        </div>
      </div>

      {/* Streamed Transactions Table */}
      <div className="overflow-hidden rounded-lg border border-gray-800 bg-[#0f141b]">
        <div className="flex items-center justify-between border-b border-gray-800 p-4">
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-blue-400" />
            <h3 className="text-sm font-medium text-white">Live Ingestion Feed</h3>
            <span className="rounded-full bg-blue-500/10 px-2 py-0.5 text-[11px] text-blue-400">
              {transactions.length} buffered
            </span>
          </div>

          <div className="flex items-center gap-2 text-xs text-gray-400">
            {status === "connected" && !isPaused && (
              <span className="flex items-center gap-1.5 text-green-400">
                <span className="h-2 w-2 rounded-full bg-green-400 animate-ping" />
                Live Feed Active
              </span>
            )}
            {isPaused && (
              <span className="text-yellow-400">Stream Paused</span>
            )}
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="border-b border-gray-800 bg-[#0c1117]">
              <tr>
                <th className="px-4 py-3 text-xs font-medium uppercase tracking-wider text-gray-500">
                  Transaction
                </th>
                <th className="px-4 py-3 text-xs font-medium uppercase tracking-wider text-gray-500">
                  Step
                </th>
                <th className="px-4 py-3 text-xs font-medium uppercase tracking-wider text-gray-500">
                  ML Score (P1)
                </th>
                <th className="px-4 py-3 text-xs font-medium uppercase tracking-wider text-gray-500">
                  Temporal Score (P1)
                </th>
                <th className="px-4 py-3 text-xs font-medium uppercase tracking-wider text-gray-500">
                  Fused Risk (P2)
                </th>
                <th className="px-4 py-3 text-xs font-medium uppercase tracking-wider text-gray-500">
                  Risk Level
                </th>
                <th className="px-4 py-3 text-xs font-medium uppercase tracking-wider text-gray-500">
                  Recommendation
                </th>
                <th className="px-4 py-3 text-xs font-medium uppercase tracking-wider text-gray-500">
                  Evidence
                </th>
              </tr>
            </thead>

            <tbody className="divide-y divide-gray-800">
              {transactions.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-4 py-10 text-center text-xs text-gray-500">
                    Awaiting transactions from WebSocket stream...
                  </td>
                </tr>
              ) : (
                transactions.map((tx) => (
                  <tr
                    key={tx.id}
                    className="transition-colors hover:bg-white/[0.02]"
                  >
                    {/* Tx ID */}
                    <td className="px-4 py-3 font-mono text-xs text-gray-300">
                      {tx.id}
                    </td>

                    {/* Step */}
                    <td className="px-4 py-3 font-mono text-xs text-gray-400">
                      {tx.time_step}
                    </td>

                    {/* ML Score */}
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-1.5">
                        <span className="font-mono text-xs text-white">
                          {tx.ml_score !== undefined ? tx.ml_score.toFixed(4) : "—"}
                        </span>
                        <span
                          className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${
                            tx.predicted_class === "ILLICIT"
                              ? "bg-red-500/20 text-red-400"
                              : "bg-green-500/20 text-green-400"
                          }`}
                        >
                          {tx.predicted_class || "—"}
                        </span>
                      </div>
                    </td>

                    {/* Temporal Score */}
                    <td className="px-4 py-3 font-mono text-xs text-purple-400">
                      {tx.temporal_score !== undefined
                        ? tx.temporal_score.toFixed(4)
                        : "—"}
                    </td>

                    {/* Fused Risk */}
                    <td className="px-4 py-3 font-mono text-xs font-semibold text-white">
                      {tx.risk_score.toFixed(1)}
                    </td>

                    {/* Risk Level */}
                    <td className="px-4 py-3">
                      <span
                        className={`rounded border px-2 py-0.5 text-xs font-medium ${
                          riskStyles[tx.risk_level]
                        }`}
                      >
                        {tx.risk_level}
                      </span>
                    </td>

                    {/* Recommendation */}
                    <td className="px-4 py-3 text-xs">
                      <span
                        className={`rounded px-2 py-1 font-medium ${
                          tx.recommended_action === "INVESTIGATE"
                            ? "bg-red-500/10 text-red-400"
                            : tx.recommended_action === "REVIEW"
                            ? "bg-orange-500/10 text-orange-400"
                            : tx.recommended_action === "MONITOR"
                            ? "bg-blue-500/10 text-blue-400"
                            : "bg-gray-800 text-gray-400"
                        }`}
                      >
                        {tx.recommended_action || "NO_ACTION"}
                      </span>
                    </td>

                    {/* Evidence Tags */}
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap gap-1">
                        {tx.evidence && tx.evidence.length > 0 ? (
                          tx.evidence.map((ev, idx) => (
                            <span
                              key={idx}
                              className="rounded border border-gray-700 bg-gray-800/40 px-1.5 py-0.5 text-[10px] text-gray-400"
                              title={ev.message}
                            >
                              {ev.category}
                            </span>
                          ))
                        ) : (
                          <span className="text-[11px] text-gray-600">—</span>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
