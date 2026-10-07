import { useState } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { Search } from "lucide-react";

import AppLayout from "./components/layout/AppLayout";
import Dashboard from "./pages/Dashboard";
import LiveMonitor from "./pages/LiveMonitor";
import AlertsPage from "./pages/AlertsPage";
import NetworkGraph from "./components/layout/dashboard/alerts/network/NetworkGraph";
import { StreamProvider } from "./context/StreamContext";

function Network() {
  const [selectedTxId, setSelectedTxId] = useState<string>("3321");
  const [inputTxId, setInputTxId] = useState<string>("");

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputTxId.trim()) {
      setSelectedTxId(inputTxId.trim());
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-white">
            Network Explorer
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Explore transaction and entity relationships with Person 2 graph intelligence
          </p>
        </div>

        <form onSubmit={handleSearch} className="flex items-center gap-2">
          <div className="relative">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-gray-500" />
            <input
              type="text"
              placeholder="Inspect Tx ID (e.g. 3321)..."
              value={inputTxId}
              onChange={(e) => setInputTxId(e.target.value)}
              className="rounded-lg border border-gray-800 bg-[#0f141b] py-2 pl-9 pr-3 text-xs text-white placeholder-gray-500 focus:border-blue-500 focus:outline-none"
            />
          </div>
          <button
            type="submit"
            className="rounded-lg bg-blue-600 px-3 py-2 text-xs font-medium text-white hover:bg-blue-500"
          >
            Inspect
          </button>
        </form>
      </div>

      <div className="rounded-lg border border-gray-800 bg-[#0f141b] p-4">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-medium text-white">
              Transaction Network (Target: {selectedTxId})
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

        <NetworkGraph txId={selectedTxId} />
      </div>
    </div>
  );
}

function App() {
  return (
    <StreamProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<AppLayout />}>
            <Route
              path="/"
              element={<Navigate to="/dashboard" replace />}
            />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/live" element={<LiveMonitor />} />
            <Route path="/alerts" element={<AlertsPage />} />
            <Route path="/network" element={<Network />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </StreamProvider>
  );
}

export default App;