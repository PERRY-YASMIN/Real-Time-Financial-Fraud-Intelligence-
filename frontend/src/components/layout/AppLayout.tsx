import { NavLink, Outlet } from "react-router-dom";
import {
  Activity,
  Bell,
  LayoutDashboard,
  Network,
} from "lucide-react";

import { useStream } from "../../context/StreamContext";

const navigation = [
  {
    name: "Dashboard",
    path: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    name: "Live Monitor",
    path: "/live",
    icon: Activity,
  },
  {
    name: "Alerts",
    path: "/alerts",
    icon: Bell,
  },
  {
    name: "Network",
    path: "/network",
    icon: Network,
  },
];

export default function AppLayout() {
  const { status } = useStream();
  return (
    <div className="min-h-screen bg-[#0b0f14] text-gray-100">
      <div className="flex min-h-screen">

        {/* Sidebar */}
        <aside className="w-60 border-r border-gray-800 bg-[#0f141b]">
          
          {/* Logo / title */}
          <div className="border-b border-gray-800 px-5 py-5">
            <h1 className="text-sm font-semibold tracking-wide">
              FINANCIAL CRIME
            </h1>

            <p className="mt-1 text-xs text-gray-500">
              Intelligence Console
            </p>
          </div>

          {/* Navigation */}
          <nav className="p-3">
            {navigation.map((item) => {
              const Icon = item.icon;

              return (
                <NavLink
                  key={item.name}
                  to={item.path}
                  className={({ isActive }) =>
                    `mb-1 flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors ${
                      isActive
                        ? "bg-gray-800 text-white"
                        : "text-gray-400 hover:bg-gray-800/50 hover:text-white"
                    }`
                  }
                >
                  <Icon size={16} />
                  {item.name}
                </NavLink>
              );
            })}
          </nav>
        </aside>

        {/* Main area */}
        <main className="flex-1">

          {/* Top bar */}
          <header className="flex h-14 items-center justify-between border-b border-gray-800 bg-[#0b0f14] px-6">
            <span className="text-sm text-gray-400">
              Analyst Workspace
            </span>

            <div className="flex items-center gap-2 text-xs">
              {status === "connected" && (
                <div className="flex items-center gap-2 text-green-400">
                  <span className="h-2 w-2 rounded-full bg-green-400 animate-pulse" />
                  SYSTEM ONLINE (STREAMING)
                </div>
              )}
              {status === "connecting" && (
                <div className="flex items-center gap-2 text-yellow-400">
                  <span className="h-2 w-2 rounded-full bg-yellow-400 animate-ping" />
                  CONNECTING...
                </div>
              )}
              {status === "disconnected" && (
                <div className="flex items-center gap-2 text-gray-400">
                  <span className="h-2 w-2 rounded-full bg-gray-500" />
                  OFFLINE (RECONNECTING)
                </div>
              )}
              {status === "error" && (
                <div className="flex items-center gap-2 text-red-400">
                  <span className="h-2 w-2 rounded-full bg-red-400" />
                  DISCONNECTED
                </div>
              )}
            </div>
          </header>

          {/* Page content */}
          <div className="p-6">
            <Outlet />
          </div>

        </main>
      </div>
    </div>
  );
}