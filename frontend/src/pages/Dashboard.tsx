import StatCard from "../components/layout/dashboard/StatCard";
import RiskTrendChart from "../components/layout/dashboard/RiskTrendChart";
import RiskDistribution from "../components/layout/dashboard/RiskDistribution";
import RecentAlerts from "../components/layout/dashboard/RecentAlerts";
import { mockDashboard } from "../mocks/data";
import { useStream } from "../context/StreamContext";


export default function Dashboard() {
  const { dashboard } = useStream();
  const data =
    dashboard.total_transactions > 0 || dashboard.active_alerts > 0
      ? dashboard
      : mockDashboard;

  return (
    <div className="space-y-6">

      {/* Page heading */}
      <div>
        <h2 className="text-2xl font-semibold text-white">
          Financial Crime Dashboard
        </h2>

        <p className="mt-1 text-sm text-gray-500">
          Real-time overview of transaction risk and suspicious activity
        </p>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Transactions"
          value={data.total_transactions}
          description="Processed transactions"
          accent="blue"
        />

        <StatCard
          label="Active Alerts"
          value={data.active_alerts}
          description="Requiring analyst review"
          accent="yellow"
        />

        <StatCard
          label="Critical Alerts"
          value={data.critical_alerts}
          description="High-priority investigations"
          accent="red"
        />

        <StatCard
          label="Suspicious Communities"
          value={data.suspicious_communities}
          description="Detected network clusters"
          accent="purple"
        />
      </div>

      {/* Placeholder for charts */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">

        <div className="rounded-lg border border-gray-800 bg-[#0f141b] p-5">
  <div className="mb-4">
    <h3 className="text-sm font-medium text-white">
      Risk Over Time
    </h3>

    <p className="mt-1 text-xs text-gray-500">
      Average transaction risk by time step
    </p>
  </div>

  <RiskTrendChart />
</div>

        <div className="rounded-lg border border-gray-800 bg-[#0f141b] p-5">
  <div className="mb-4">
    <h3 className="text-sm font-medium text-white">
      Risk Distribution
    </h3>

    <p className="mt-1 text-xs text-gray-500">
      Transactions grouped by risk level
    </p>
  </div>

  <RiskDistribution />
</div>

      </div>
      {/* Recent Alerts */}
      <RecentAlerts alerts={data.recent_alerts} />

    </div>
  );
}