import React, { useState, useMemo, useEffect } from "react";
import {
  Search,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
} from "lucide-react";

const SEVERITIES = ["All Severities", "Critical", "High", "Medium", "Low"];
const PAGE_SIZE_OPTIONS = [10, 25, 50, 100, "All"];

const DUMMY_INCIDENTS = [
  { id: "INC-1001", incident_type: "Fire", location: "Main St & 5th Ave", time: "12/02/2026, 08:23:00", severity: "CRITICAL", confidence: "94%", status: "Dispatched" },
  { id: "INC-1002", incident_type: "Medical", location: "Oak Park, Zone B", time: "12/02/2026, 07:45:00", severity: "HIGH", confidence: "87%", status: "Active" },
  { id: "INC-1003", incident_type: "Traffic", location: "Highway 101, Mile 34", time: "12/02/2026, 07:12:00", severity: "MEDIUM", confidence: "78%", status: "Dispatched" },
  { id: "INC-1004", incident_type: "Rescue", location: "Riverside Trail", time: "12/02/2026, 06:55:00", severity: "LOW", confidence: "91%", status: "Resolved" },
  { id: "INC-1005", incident_type: "Fire", location: "Industrial Park E", time: "12/02/2026, 06:30:00", severity: "HIGH", confidence: "82%", status: "Dispatched" },
  { id: "INC-1006", incident_type: "Medical", location: "Central Mall", time: "12/02/2026, 05:48:00", severity: "LOW", confidence: "95%", status: "Closed" },
  { id: "INC-1007", incident_type: "Traffic", location: "Elm St & 3rd Ave", time: "12/02/2026, 05:15:00", severity: "MEDIUM", confidence: "72%", status: "Resolved" },
  { id: "INC-1008", incident_type: "Fire", location: "Sunset Blvd 120", time: "12/02/2026, 04:40:00", severity: "CRITICAL", confidence: "96%", status: "Active" },
  { id: "INC-1009", incident_type: "Rescue", location: "Lake District", time: "11/02/2026, 23:10:00", severity: "HIGH", confidence: "80%", status: "Closed" },
  { id: "INC-1010", incident_type: "Fire", location: "Main St & 5th Ave", time: "12/02/2026, 08:23:00", severity: "CRITICAL", confidence: "94%", status: "Dispatched" },
  { id: "INC-1012", incident_type: "Medical", location: "Oak Park, Zone B", time: "12/02/2026, 07:45:00", severity: "HIGH", confidence: "87%", status: "Active" },
  { id: "INC-1013", incident_type: "Traffic", location: "Highway 101, Mile 34", time: "12/02/2026, 07:12:00", severity: "MEDIUM", confidence: "78%", status: "Dispatched" },
  { id: "INC-1014", incident_type: "Rescue", location: "Riverside Trail", time: "12/02/2026, 06:55:00", severity: "LOW", confidence: "91%", status: "Resolved" },
  { id: "INC-1015", incident_type: "Fire", location: "Industrial Park E", time: "12/02/2026, 06:30:00", severity: "HIGH", confidence: "82%", status: "Dispatched" },
  { id: "INC-1016", incident_type: "Medical", location: "Central Mall", time: "12/02/2026, 05:48:00", severity: "LOW", confidence: "95%", status: "Closed" },
  { id: "INC-1017", incident_type: "Traffic", location: "Elm St & 3rd Ave", time: "12/02/2026, 05:15:00", severity: "MEDIUM", confidence: "72%", status: "Resolved" },
  { id: "INC-1018", incident_type: "Fire", location: "Sunset Blvd 120", time: "12/02/2026, 04:40:00", severity: "CRITICAL", confidence: "96%", status: "Active" },
  { id: "INC-1019", incident_type: "Rescue", location: "Lake District", time: "11/02/2026, 23:10:00", severity: "HIGH", confidence: "80%", status: "Closed" },
]

function SeverityBadge({ severity }) {
  // Dark mode: colored pill with dark interior, light border; light mode: softer variant
  const base =
    "inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-semibold tracking-wide border transition-colors transition-shadow duration-200";

  const severityStyles = {
    CRITICAL:
      // light
      "border-red-300 bg-red-50 text-red-600 " +
      // dark + hover glow
      "dark:border-red-500 dark:bg-red-500/10 dark:text-red-300 " +
      "hover:bg-red-50 dark:hover:bg-red-500/20 hover:shadow-[0_0_26px_rgba(248,113,113,0.9)]",
    HIGH:
      "border-orange-300 bg-orange-50 text-orange-600 " +
      "dark:border-orange-500 dark:bg-orange-500/10 dark:text-orange-300",
    MEDIUM:
      "border-amber-300 bg-amber-50 text-amber-600 " +
      "dark:border-amber-500 dark:bg-amber-500/10 dark:text-amber-300",
    LOW:
      "border-emerald-300 bg-emerald-50 text-emerald-600 " +
      "dark:border-emerald-500 dark:bg-emerald-500/10 dark:text-emerald-300",
  };

  const dotColors = {
    CRITICAL: "bg-red-500",
    HIGH: "bg-orange-400",
    MEDIUM: "bg-amber-400",
    LOW: "bg-emerald-400",
  };

  const cls = `${base} ${
    severityStyles[severity] || "border-slate-300 bg-slate-50 text-slate-500"
  }`;
  const dot = dotColors[severity] || "bg-slate-400";

  return (
    <span className={cls}>
      <span className={`w-2.5 h-2.5 rounded-full ${dot}`} />
      <span className="uppercase">{severity}</span>
    </span>
  );
}

export default function History() {
  const [search, setSearch] = useState("");
  const [severityFilter, setSeverityFilter] = useState("All Severities");
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [pageSize, setPageSize] = useState(10);
  const [currentPage, setCurrentPage] = useState(1);

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    const activeSeverity =
      severityFilter === "All Severities"
        ? null
        : severityFilter.toUpperCase();

    return DUMMY_INCIDENTS.filter((row) => {
      const matchSearch =
        !q ||
        row.id.toLowerCase().includes(q) ||
        row.location.toLowerCase().includes(q) ||
        row.incident_type.toLowerCase().includes(q) ||
        row.severity.toLowerCase().includes(q);

      const matchSeverity = !activeSeverity || row.severity === activeSeverity;

      return matchSearch && matchSeverity;
    });
  }, [search, severityFilter]);

  const totalFiltered = filtered.length;

  useEffect(() => {
    // Reset to first page whenever filters or page size change
    setCurrentPage(1);
  }, [search, severityFilter, pageSize]);

  const pageCount =
    pageSize === null || totalFiltered === 0
      ? 1
      : Math.max(1, Math.ceil(totalFiltered / pageSize));

  const paginated = useMemo(() => {
    if (pageSize === null) return filtered;
    const start = (currentPage - 1) * pageSize;
    const end = start + pageSize;
    return filtered.slice(start, end);
  }, [filtered, currentPage, pageSize]);

  const startIndex =
    totalFiltered === 0
      ? 0
      : pageSize === null
      ? 1
      : (currentPage - 1) * pageSize + 1;

  const endIndex =
    totalFiltered === 0
      ? 0
      : pageSize === null
      ? totalFiltered
      : Math.min(totalFiltered, currentPage * pageSize);

  return (
    <div className="min-h-screen bg-[#F4F6F8] dark:bg-[#0F172A] text-[#1A1A1A] dark:text-[#F1F5F9] p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white tracking-tight">
          Incident History
        </h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-slate-400">
          Browse and filter past incident records
        </p>
      </div>

      {/* Search and filter — long search bar + severities dropdown */}
      <div className="flex items-center gap-3 mb-6 w-full flex-wrap">
        <div className="relative flex-1 min-w-[700px]">
          <Search
            className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-slate-500 shrink-0 pointer-events-none"
            strokeWidth={2}
          />
          <input
            type="text"
            placeholder="Search by ID or Location..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-20 pr-4 py-3 rounded-xl bg-[#F0F2F5] dark:bg-slate-800 border border-gray-200 dark:border-slate-600 text-gray-900 dark:text-slate-100 placeholder-gray-500 dark:placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-300 dark:focus:ring-slate-500 focus:border-transparent"
          />
        </div>
        <div className="relative">
          <button
            type="button"
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              setDropdownOpen((o) => !o);
            }}
            className="flex items-center gap-2 px-5 py-3 rounded-xl bg-[#F0F2F5] dark:bg-slate-800 border border-gray-200 dark:border-slate-600 text-gray-700 dark:text-slate-200 min-w-[180px] justify-between hover:bg-gray-200 dark:hover:bg-slate-700 transition-colors"
          >
            <span>{severityFilter}</span>
            <ChevronDown className="w-5 h-5 text-gray-500 dark:text-slate-400 shrink-0" />
          </button>
          {dropdownOpen && (
            <>
              <div
                className="fixed inset-0 z-[100]"
                aria-hidden="true"
                onClick={() => setDropdownOpen(false)}
              />
              <ul className="absolute top-full left-0 mt-2 min-w-[180px] rounded-xl bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-600 shadow-lg z-[101] py-1 max-h-60 overflow-auto">
                {SEVERITIES.map((s) => (
                  <li key={s}>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.preventDefault();
                        setSeverityFilter(s);
                        setDropdownOpen(false);
                      }}
                      className={`w-full text-left px-4 py-2.5 text-sm transition-colors ${
                        severityFilter === s
                          ? "bg-gray-100 dark:bg-slate-700 text-gray-900 dark:text-white font-medium"
                          : "text-gray-700 dark:text-slate-300 hover:bg-gray-100 dark:hover:bg-slate-700"
                      }`}
                    >
                      {s}
                    </button>
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>
      </div>

      {/* Table */}
      <div className="rounded-xl border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800/50 overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-gray-200 dark:border-slate-700 bg-gray-50/80 dark:bg-slate-800/80">
                <th className="px-5 py-3.5 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-slate-400">
                  ID
                </th>
                <th className="px-5 py-3.5 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-slate-400">
                  Type
                </th>
                <th className="px-5 py-3.5 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-slate-400">
                  Location
                </th>
                <th className="px-5 py-3.5 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-slate-400">
                  Time
                </th>
                <th className="px-5 py-3.5 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-slate-400">
                  Severity
                </th>
                <th className="px-5 py-3.5 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-slate-400">
                  Confidence
                </th>
                <th className="px-5 py-3.5 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-slate-400">
                  Status
                </th>
              </tr>
            </thead>
            <tbody>
              {paginated.map((row, i) => (
                <tr
                  key={row.id}
                  className={`border-b border-gray-100 dark:border-slate-700/80 transition-colors ${
                    i % 2 === 0
                      ? "bg-white dark:bg-slate-800/30"
                      : "bg-gray-50/50 dark:bg-slate-800/50"
                  }`}
                >
                  <td className="px-5 py-3.5">
                    <span className="text-red-500 dark:text-red-400 font-medium cursor-pointer hover:underline">
                      {row.id}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 text-gray-900 dark:text-slate-200">
                    {row.incident_type}
                  </td>
                  <td className="px-5 py-3.5 text-gray-900 dark:text-slate-200">
                    {row.location}
                  </td>
                  <td className="px-5 py-3.5 text-gray-900 dark:text-slate-200">
                    {row.time}
                  </td>
                  <td className="px-5 py-3.5">
                    <SeverityBadge severity={row.severity} />
                  </td>
                  <td className="px-5 py-3.5 text-gray-900 dark:text-slate-200">
                    {row.confidence}
                  </td>
                  <td className="px-5 py-3.5 text-gray-900 dark:text-slate-200">
                    {row.status}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {filtered.length === 0 && (
          <div className="px-5 py-12 text-center text-gray-500 dark:text-slate-400">
            No incidents match your filters.
          </div>
        )}

        {filtered.length > 0 && (
          <div className="flex items-center justify-between gap-4 px-5 py-3 border-t border-gray-100 dark:border-slate-700 text-xs">
            {/* Rows per page selector */}
            <div className="flex items-center gap-2 text-gray-600 dark:text-slate-400">
              <span className="hidden sm:inline">Rows per page</span>
              <select
                value={pageSize === null ? "All" : String(pageSize)}
                onChange={(e) => {
                  const value = e.target.value;
                  if (value === "All") {
                    setPageSize(null);
                  } else {
                    setPageSize(Number(value));
                  }
                }}
                className="h-8 rounded-md border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-2 pr-6 text-xs text-gray-700 dark:text-slate-100 focus:outline-none focus:ring-1 focus:ring-slate-400 dark:focus:ring-slate-500"
              >
                {PAGE_SIZE_OPTIONS.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt}
                  </option>
                ))}
              </select>
            </div>

            {/* Range text */}
            <div className="flex-1 text-center text-gray-500 dark:text-slate-400">
              {startIndex}-{endIndex} of {totalFiltered}
            </div>

            {/* Pagination controls */}
            <div className="flex items-center gap-1 text-gray-600 dark:text-slate-400">
              <button
                type="button"
                onClick={() => setCurrentPage(1)}
                disabled={pageSize === null || currentPage === 1}
                className="p-1.5 rounded-md border border-transparent hover:bg-gray-100 dark:hover:bg-slate-700 disabled:opacity-40 disabled:hover:bg-transparent disabled:cursor-not-allowed"
              >
                <ChevronsLeft className="w-4 h-4" />
              </button>
              <button
                type="button"
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={pageSize === null || currentPage === 1}
                className="p-1.5 rounded-md border border-transparent hover:bg-gray-100 dark:hover:bg-slate-700 disabled:opacity-40 disabled:hover:bg-transparent disabled:cursor-not-allowed"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                type="button"
                onClick={() =>
                  setCurrentPage((p) => Math.min(pageCount, p + 1))
                }
                disabled={pageSize === null || currentPage >= pageCount}
                className="p-1.5 rounded-md border border-transparent hover:bg-gray-100 dark:hover:bg-slate-700 disabled:opacity-40 disabled:hover:bg-transparent disabled:cursor-not-allowed"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
              <button
                type="button"
                onClick={() => setCurrentPage(pageCount)}
                disabled={pageSize === null || currentPage >= pageCount}
                className="p-1.5 rounded-md border border-transparent hover:bg-gray-100 dark:hover:bg-slate-700 disabled:opacity-40 disabled:hover:bg-transparent disabled:cursor-not-allowed"
              >
                <ChevronsRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
