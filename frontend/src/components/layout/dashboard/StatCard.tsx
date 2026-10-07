interface StatCardProps {
  label: string;
  value: number;
  description?: string;
  accent?: "blue" | "yellow" | "red" | "purple";
}

const accentStyles = {
  blue: "text-blue-400 bg-blue-400/10 border-blue-400/20",
  yellow: "text-yellow-400 bg-yellow-400/10 border-yellow-400/20",
  red: "text-red-400 bg-red-400/10 border-red-400/20",
  purple: "text-purple-400 bg-purple-400/10 border-purple-400/20",
};

export default function StatCard({
  label,
  value,
  description,
  accent = "blue",
}: StatCardProps) {
  return (
    <div className="rounded-lg border border-gray-800 bg-[#0f141b] p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-gray-500">
            {label}
          </p>

          <p className="mt-2 text-3xl font-semibold text-white">
            {value.toLocaleString()}
          </p>

          {description && (
            <p className="mt-1 text-xs text-gray-500">
              {description}
            </p>
          )}
        </div>

        <div
          className={`rounded-md border px-2 py-1 text-xs ${accentStyles[accent]}`}
        >
          LIVE
        </div>
      </div>
    </div>
  );
}