import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import AppLayout from "./components/layout/AppLayout";


import Dashboard from "./pages/Dashboard"; 
import NetworkGraph from "./components/layout/dashboard/alerts/network/NetworkGraph";

function LiveMonitor() {
  return (
    <div>
      <h2 className="text-2xl font-semibold text-white">
        Live Monitor
      </h2>

      <p className="mt-2 text-sm text-gray-400">
        Real-time transaction monitoring
      </p>
    </div>
  );
}

function Alerts() {
  return (
    <div>
      <h2 className="text-2xl font-semibold text-white">
        Alerts
      </h2>

      <p className="mt-2 text-sm text-gray-400">
        Suspicious activity alerts
      </p>
    </div>
  );
}

function Network() {
   return (
    <div className="space-y-6">

      <div>
        <h2 className="text-2xl font-semibold text-white">
          Network Explorer
        </h2>

        <p className="mt-1 text-sm text-gray-500">
          Explore transaction and entity relationships
        </p>
      </div>

      <div className="rounded-lg border border-gray-800 bg-[#0f141b] p-4">

        <div className="mb-4 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-medium text-white">
              Transaction Network
            </h3>

            <p className="mt-1 text-xs text-gray-500">
              Nodes represent entities and edges represent transaction relationships
            </p>
          </div>

          <div className="flex gap-4 text-xs">
            <span className="text-green-400">● Low</span>
            <span className="text-blue-400">● Medium</span>
            <span className="text-orange-400">● High</span>
            <span className="text-red-400">● Critical</span>
          </div>
        </div>

        <NetworkGraph />

      </div>

    </div>
   );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route
            path="/"
            element={<Navigate to="/dashboard" replace />}
          />

          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/live" element={<LiveMonitor />} />
          <Route path="/alerts" element={<Alerts />} />
          <Route path="/network" element={<Network />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;