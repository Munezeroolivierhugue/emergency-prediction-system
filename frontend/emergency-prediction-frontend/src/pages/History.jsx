import React, { useState, useEffect, useCallback } from "react";
import {
  Search,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
} from "lucide-react";
import { incidentService } from "../utils/api";
import { DUMMY_INCIDENTS } from "../utils/dummyData";

const SEVERITIES = ["All Severities", "Critical", "High", "Medium", "Low"];
const PAGE_SIZE_OPTIONS = [10, 25, 50, 100];


function SeverityBadge({ severity }) {
  // Dark mode: colored pill with dark interior, light border; light mode: softer variant
  const base =
    "inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-semibold tracking-wide border transition-colors transition-shadow duration-200";

  const severityStyles = {
    critical:
      // light
      "border-red-300 bg-red-50 text-red-600 " +
      // dark + hover glow
      "dark:border-red-500 dark:bg-red-500/10 dark:text-red-300 " +
      "hover:bg-red-50 dark:hover:bg-red-500/20 hover:shadow-[0_0_26px_rgba(248,113,113,0.9)]",
    high:
      "border-orange-300 bg-orange-50 text-orange-600 " +
      "dark:border-orange-500 dark:bg-orange-500/10 dark:text-orange-300",
    medium:
      "border-amber-300 bg-amber-50 text-amber-600 " +
      "dark:border-amber-500 dark:bg-amber-500/10 dark:text-amber-300",
    low:
      "border-emerald-300 bg-emerald-50 text-emerald-600 " +
      "dark:border-emerald-500 dark:bg-emerald-500/10 dark:text-emerald-300",
  };

  const dotColors = {
    critical: "bg-red-500",
    high: "bg-orange-400",
    medium: "bg-amber-400",
    low: "bg-emerald-400",
  };

  const key = (severity || "").toLowerCase();
  const cls = `${base} ${severityStyles[key] || "border-slate-300 bg-slate-50 text-slate-500"
    }`;
  const dot = dotColors[key] || "bg-slate-400";

  return (
    <span className={cls}>
      <span className={`w-2.5 h-2.5 rounded-full ${dot}`} />
      <span className="uppercase">{severity}</span>
    </span>
  );
}

export default function History() {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [severityFilter, setSeverityFilter] = useState("All Severities");
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [pageSize, setPageSize] = useState(10);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);

  const fetchIncidents = useCallback(async () => {
    setLoading(true);
    try {
      const params = {
        page: currentPage,
        page_size: pageSize,
      };
      if (search) params.search = search;
      if (severityFilter !== "All Severities") params.severity = severityFilter;

      const response = await incidentService.getIncidents(params);
      setIncidents(response.data.results || []);
      setTotalCount(response.data.count || 0);
    } catch (error) {
      console.error("Error fetching incidents:", error);
      // Fallback to dummy data
      setIncidents(DUMMY_INCIDENTS);
      setTotalCount(DUMMY_INCIDENTS.length);
    } finally {
      setLoading(false);
    }
  }, [currentPage, pageSize, search, severityFilter]);

  useEffect(() => {
    fetchIncidents();
  }, [fetchIncidents]);

  useEffect(() => {
    // Reset to first page whenever filters or page size change
    setCurrentPage(1);
  }, [search, severityFilter, pageSize]);

  const pageCount = Math.max(1, Math.ceil(totalCount / pageSize));

  const startIndex = totalCount === 0 ? 0 : (currentPage - 1) * pageSize + 1;
  const endIndex = Math.min(totalCount, currentPage * pageSize);

  return (
    <div className="min-h-screen bg-[#F4F6F8] dark:bg-[#0F172A] text-[#1A1A1A] dark:text-[#F1F5F9] p-4 sm:p-6">
      {/* Header */}
      <div className="mb-6 sm:mb-8">
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white tracking-tight">
          Incident History
        </h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-slate-400">
          Browse and filter past incident records
        </p>
      </div>

      {/* Search and filter */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 mb-6 w-full">
        <div className="relative flex-1 min-w-0">
          <Search
            className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-slate-500 shrink-0 pointer-events-none"
            strokeWidth={2}
          />
          <input
            type="text"
            placeholder="Search by ID or Location..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 sm:pl-20 pr-4 py-3 rounded-xl bg-[#F0F2F5] dark:bg-slate-800 border border-gray-200 dark:border-slate-600 text-gray-900 dark:text-slate-100 placeholder-gray-500 dark:placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-300 dark:focus:ring-slate-500 focus:border-transparent text-sm sm:text-base"
          />
        </div>
        <div className="relative w-full sm:w-auto">
          <button
            type="button"
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              setDropdownOpen((o) => !o);
            }}
            className="flex items-center gap-2 px-5 py-3 rounded-xl bg-[#F0F2F5] dark:bg-slate-800 border border-gray-200 dark:border-slate-600 text-gray-700 dark:text-slate-200 w-full sm:min-w-[180px] justify-between hover:bg-gray-200 dark:hover:bg-slate-700 transition-colors text-sm sm:text-base"
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
              <ul className="absolute top-full left-0 mt-2 w-full sm:min-w-[180px] rounded-xl bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-600 shadow-lg z-[101] py-1 max-h-60 overflow-auto">
                {SEVERITIES.map((s) => (
                  <li key={s}>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.preventDefault();
                        setSeverityFilter(s);
                        setDropdownOpen(false);
                      }}
                      className={`w-full text-left px-4 py-2.5 text-sm transition-colors ${severityFilter === s
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
              {loading ? (
                <tr>
                  <td colSpan="7" className="py-20 text-center">
                    <div className="flex flex-col items-center gap-2">
                      <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
                      <span className="text-sm text-gray-500">Loading incidents...</span>
                    </div>
                  </td>
                </tr>
              ) : incidents.length === 0 ? (
                <tr>
                  <td colSpan="7" className="py-20 text-center text-gray-500">
                    No incidents match your filters.
                  </td>
                </tr>
              ) : (
                incidents.map((row, i) => {
                  const displayId = typeof row.id === 'number' ? `INC-${row.id}` : row.id;
                  const displayTime = row.timestamp ? new Date(row.timestamp).toLocaleString() : (row.time || "N/A");

                  return (
                    <tr
                      key={row.id}
                      className={`border-b border-gray-100 dark:border-slate-700/80 transition-colors ${i % 2 === 0
                        ? "bg-white dark:bg-slate-800/30"
                        : "bg-gray-50/50 dark:bg-slate-800/50"
                        }`}
                    >
                      <td className="px-5 py-3.5">
                        <span className="text-red-500 dark:text-red-400 font-medium cursor-pointer hover:underline">
                          {displayId}
                        </span>
                      </td>
                      <td className="px-5 py-3.5 text-gray-900 dark:text-slate-200">
                        {row.type || row.incident_type}
                      </td>
                      <td className="px-5 py-3.5 text-gray-900 dark:text-slate-200">
                        {row.location || row.twp || "Unknown"}
                      </td>
                      <td className="px-5 py-3.5 text-gray-900 dark:text-slate-200">
                        {displayTime}
                      </td>
                      <td className="px-5 py-3.5">
                        <SeverityBadge severity={row.severity} />
                      </td>
                      <td className="px-5 py-3.5 text-gray-900 dark:text-slate-200">
                        {row.confidence || "N/A"}
                      </td>
                      <td className="px-5 py-3.5 text-gray-900 dark:text-slate-200">
                        {row.status || "Resolved"}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
        {totalCount > 0 && (
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 px-4 sm:px-5 py-3 border-t border-gray-100 dark:border-slate-700 text-xs">
            {/* Rows per page selector */}
            <div className="flex items-center gap-2 text-gray-600 dark:text-slate-400">
              <span className="text-xs sm:text-sm">Rows per page</span>
              <select
                value={String(pageSize)}
                onChange={(e) => {
                  setPageSize(Number(e.target.value));
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
            <div className="flex-1 text-center text-gray-500 dark:text-slate-400 text-xs sm:text-sm">
              {startIndex}-{endIndex} of {totalCount}
            </div>

            {/* Pagination controls */}
            <div className="flex items-center gap-1 text-gray-600 dark:text-slate-400">
              <button
                type="button"
                onClick={() => setCurrentPage(1)}
                disabled={currentPage === 1}
                className="p-1.5 rounded-md border border-transparent hover:bg-gray-100 dark:hover:bg-slate-700 disabled:opacity-40 disabled:hover:bg-transparent disabled:cursor-not-allowed"
              >
                <ChevronsLeft className="w-4 h-4" />
              </button>
              <button
                type="button"
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="p-1.5 rounded-md border border-transparent hover:bg-gray-100 dark:hover:bg-slate-700 disabled:opacity-40 disabled:hover:bg-transparent disabled:cursor-not-allowed"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                type="button"
                onClick={() =>
                  setCurrentPage((p) => Math.min(pageCount, p + 1))
                }
                disabled={currentPage >= pageCount}
                className="p-1.5 rounded-md border border-transparent hover:bg-gray-100 dark:hover:bg-slate-700 disabled:opacity-40 disabled:hover:bg-transparent disabled:cursor-not-allowed"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
              <button
                type="button"
                onClick={() => setCurrentPage(pageCount)}
                disabled={currentPage >= pageCount}
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
