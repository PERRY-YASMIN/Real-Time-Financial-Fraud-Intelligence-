import { Bell, ShieldAlert, AlertTriangle } from "lucide-react";
import RecentAlerts from "../components/layout/dashboard/RecentAlerts";
import { useStream } from "../context/StreamContext";

export default function AlertsPage() {
  const { alerts, dashboard } = useStream();

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-white">
          Suspicious Activity Alerts
        </h2>
        <p className="mt-1 text-sm text-gray-500">
          Prioritized alert queue evaluated by Person 2 Risk Engine combining ML, Graph, and Temporal signals
        </p>
      </div>

      {/* Alert KPI Summary */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <div className="rounded-lg border border-gray-800 bg-[#0f141b] p-4">
          <div className="flex items-center gap-2 text-yellow-400">
            <Bell size={16} />
            <span className="text-xs font-medium uppercase">Active Alerts</span>
          </div>
          <p className="mt-2 text-2xl font-bold text-white">
            {dashboard.active_alerts}
          </p>
          <p className="mt-1 text-xs text-gray-500">Awaiting triage & review</p>
        </div>

        <div className="rounded-lg border border-gray-800 bg-[#0f141b] p-4">
          <div className="flex items-center gap-2 text-red-400">
            <ShieldAlert size={16} />
            <span className="text-xs font-medium uppercase">Critical Severity</span>
          </div>
          <p className="mt-2 text-2xl font-bold text-white">
            {dashboard.critical_alerts}
          </p>
          <p className="mt-1 text-xs text-gray-500">Risk score ≥ 80 with multi-signal fusion</p>
        </div>

        <div className="rounded-lg border border-gray-800 bg-[#0f141b] p-4">
          <div className="flex items-center gap-2 text-orange-400">
            <AlertTriangle size={16} />
            <span className="text-xs font-medium uppercase">High Severity</span>
          </div>
          <p className="mt-2 text-2xl font-bold text-white">
            {alerts.filter((a) => a.risk_level === "HIGH").length}
          </p>
          <p className="mt-1 text-xs text-gray-500">Risk score 60 – 79</p>
        </div>
      </div>

      {/* Alerts Table */}
      <RecentAlerts alerts={alerts} />
    </div>
  );
}
