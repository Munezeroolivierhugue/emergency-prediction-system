import React, { useState, useEffect, useCallback } from "react";
import {
  Search,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  AlertTriangle,
  MapPin,
  Clock,
  Activity,
} from "lucide-react";
import { incidentService } from "../utils/api";
import { DUMMY_INCIDENTS } from "../utils/dummyData";

const SEVERITIES = ["All Severities", "Critical", "High", "Medium", "Low"];
const PAGE_SIZE_OPTIONS = [10, 25, 50, 100];

function SeverityBadge({ severity }) {
  const base =
    "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold tracking-wide border transition-colors duration-200";

  const severityStyles = {
    critical:
      "border-red-300 bg-red-50 text-red-600 dark:border-red-500 dark:bg-red-500/10 dark:text-red-300",
    high:
      "border-orange-300 bg-orange-50 text-orange-600 dark:border-orange-500 dark:bg-orange-500/10 dark:text-orange-300",
    medium:
      "border-amber-300 bg-amber-50 text-amber-600 dark:border-amber-500 dark:bg-amber-500/10 dark:text-amber-300",
    low:
      "border-emerald-300 bg-emerald-50 text-emerald-600 dark:border-emerald-500 dark:bg-emerald-500/10 dark:text-emerald-300",
  };

  const dotColors = {
    critical: "bg-red-500",
    high: "bg-orange-400",
    medium: "bg-amber-400",
    low: "bg-emerald-400",
  };

  const key = (severity || "").toLowerCase();
  const cls = `${base} ${severityStyles[key] || "border-slate-300 bg-slate-50 text-slate-500"}`;
  const dot = dotColors[key] || "bg-slate-400";

  return (
    <span className={cls}>
      <span className={`w-2 h-2 rounded-full ${dot}`} />
      <span className="uppercase">{severity}</span>
    </span>
  );
}

function StatusBadge({ status }) {
  const s = (status || "resolved").toLowerCase();
  const styles =
    s === "active"
      ? "bg-blue-50 text-blue-600 border border-blue-200 dark:bg-blue-500/10 dark:text-blue-300 dark:border-blue-800"
      : s === "dispatched"
        ? "bg-purple-50 text-purple-600 border border-purple-200 dark:bg-purple-500/10 dark:text-purple-300 dark:border-purple-800"
        : "bg-gray-50 text-gray-500 border border-gray-200 dark:bg-slate-500/10 dark:text-slate-400 dark:border-slate-700";
  return (
    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${styles}`}>
      {status || "Resolved"}
    </span>
  );
}

/* ── Mobile card for one incident ─────────────────────────────── */
function IncidentCard({ row, i }) {
  const displayId = typeof row.id === "number" ? `INC-${row.id}` : row.id;
  const displayTime = row.timestamp
    ? new Date(row.timestamp).toLocaleString()
    : row.time || "N/A";

  return (
    <div
      className={`p-4 rounded-xl border border-border space-y-3 ${i % 2 === 0 ? "bg-card" : "bg-muted/20"
        }`}
    >
      {/* Top row */}
      <div className="flex items-center justify-between gap-2 flex-wrap">
        <span className="text-primary font-semibold text-sm">{displayId}</span>
        <SeverityBadge severity={row.severity} />
      </div>

      {/* Type + Status */}
      <div className="flex items-center justify-between gap-2 flex-wrap">
        <span className="flex items-center gap-1.5 text-sm font-medium text-foreground">
          <Activity className="w-3.5 h-3.5 text-muted-foreground" />
          {row.type || row.incident_type || "—"}
        </span>
        <StatusBadge status={row.status} />
      </div>

      {/* Location */}
      <div className="flex items-start gap-1.5 text-xs text-muted-foreground">
        <MapPin className="w-3.5 h-3.5 mt-0.5 shrink-0" />
        <span>{row.location || row.twp || "Unknown"}</span>
      </div>

      {/* Time + Confidence */}
      <div className="flex items-center justify-between text-xs text-muted-foreground flex-wrap gap-1">
        <span className="flex items-center gap-1">
          <Clock className="w-3.5 h-3.5" />
          {displayTime}
        </span>
        {row.confidence && (
          <span className="font-semibold text-foreground">
            {row.confidence} confidence
          </span>
        )}
      </div>
    </div>
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
      const params = { page: currentPage, page_size: pageSize };
      if (search) params.search = search;
      if (severityFilter !== "All Severities") params.severity = severityFilter;

      const response = await incidentService.getIncidents(params);
      setIncidents(response.data.results || []);
      setTotalCount(response.data.count || 0);
    } catch (error) {
      console.error("Error fetching incidents:", error);
      setIncidents(DUMMY_INCIDENTS);
      setTotalCount(DUMMY_INCIDENTS.length);
    } finally {
      setLoading(false);
    }
  }, [currentPage, pageSize, search, severityFilter]);

  useEffect(() => { fetchIncidents(); }, [fetchIncidents]);
  useEffect(() => { setCurrentPage(1); }, [search, severityFilter, pageSize]);

  const pageCount = Math.max(1, Math.ceil(totalCount / pageSize));
  const startIndex = totalCount === 0 ? 0 : (currentPage - 1) * pageSize + 1;
  const endIndex = Math.min(totalCount, currentPage * pageSize);

  return (
    <div className="min-h-screen bg-background text-foreground p-3 sm:p-6">
      {/* Header */}
      <div className="mb-5 sm:mb-8">
        <h1 className="text-2xl sm:text-3xl font-bold text-foreground tracking-tight">
          Incident History
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Browse and filter past incident records
        </p>
      </div>

      {/* Search + Filter */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 mb-5 w-full">
        <div className="relative flex-1 min-w-0">
          <Search
            className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none"
            strokeWidth={2}
          />
          <input
            type="text"
            placeholder="Search by ID or Location..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2.5 rounded-xl bg-card border border-border text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50 text-sm transition"
          />
        </div>
        <div className="relative w-full sm:w-auto">
          <button
            type="button"
            onClick={(e) => { e.preventDefault(); e.stopPropagation(); setDropdownOpen((o) => !o); }}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-card border border-border text-foreground w-full sm:min-w-[175px] justify-between hover:bg-muted transition-colors text-sm"
          >
            <span>{severityFilter}</span>
            <ChevronDown className="w-4 h-4 text-muted-foreground shrink-0" />
          </button>
          {dropdownOpen && (
            <>
              <div className="fixed inset-0 z-[100]" aria-hidden="true" onClick={() => setDropdownOpen(false)} />
              <ul className="absolute top-full left-0 mt-2 w-full sm:min-w-[175px] rounded-xl bg-card border border-border shadow-lg z-[101] py-1 max-h-60 overflow-auto">
                {SEVERITIES.map((s) => (
                  <li key={s}>
                    <button
                      type="button"
                      onClick={(e) => { e.preventDefault(); setSeverityFilter(s); setDropdownOpen(false); }}
                      className={`w-full text-left px-4 py-2.5 text-sm transition-colors ${severityFilter === s
                          ? "bg-muted text-foreground font-medium"
                          : "text-muted-foreground hover:bg-muted hover:text-foreground"
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

      {/* ── MOBILE: card list (visible below sm) ──────────────── */}
      <div className="sm:hidden space-y-3 mb-4">
        {loading ? (
          <div className="flex flex-col items-center gap-3 py-16">
            <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
            <span className="text-sm text-muted-foreground">Loading incidents...</span>
          </div>
        ) : incidents.length === 0 ? (
          <div className="flex flex-col items-center gap-2 py-16 text-muted-foreground">
            <AlertTriangle className="w-8 h-8 opacity-40" />
            <span className="text-sm">No incidents match your filters.</span>
          </div>
        ) : (
          incidents.map((row, i) => <IncidentCard key={row.id} row={row} i={i} />)
        )}
      </div>

      {/* ── DESKTOP: table (visible at sm+) ───────────────────── */}
      <div className="hidden sm:block rounded-xl border border-border bg-card overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-border bg-muted/40">
                {["ID", "Type", "Location", "Time", "Severity", "Confidence", "Status"].map((h) => (
                  <th key={h} className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground whitespace-nowrap">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="7" className="py-20 text-center">
                    <div className="flex flex-col items-center gap-2">
                      <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
                      <span className="text-sm text-muted-foreground">Loading incidents...</span>
                    </div>
                  </td>
                </tr>
              ) : incidents.length === 0 ? (
                <tr>
                  <td colSpan="7" className="py-20 text-center text-muted-foreground text-sm">
                    No incidents match your filters.
                  </td>
                </tr>
              ) : (
                incidents.map((row, i) => {
                  const displayId = typeof row.id === "number" ? `INC-${row.id}` : row.id;
                  const displayTime = row.timestamp
                    ? new Date(row.timestamp).toLocaleString()
                    : row.time || "N/A";
                  return (
                    <tr
                      key={row.id}
                      className={`border-b border-border/60 transition-colors hover:bg-muted/30 ${i % 2 === 0 ? "" : "bg-muted/10"
                        }`}
                    >
                      <td className="px-4 py-3">
                        <span className="text-primary font-medium text-sm cursor-pointer hover:underline">{displayId}</span>
                      </td>
                      <td className="px-4 py-3 text-sm text-foreground">{row.type || row.incident_type}</td>
                      <td className="px-4 py-3 text-sm text-muted-foreground">{row.location || row.twp || "Unknown"}</td>
                      <td className="px-4 py-3 text-sm text-muted-foreground whitespace-nowrap">{displayTime}</td>
                      <td className="px-4 py-3"><SeverityBadge severity={row.severity} /></td>
                      <td className="px-4 py-3 text-sm text-foreground font-semibold">{row.confidence || "N/A"}</td>
                      <td className="px-4 py-3"><StatusBadge status={row.status} /></td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalCount > 0 && (
          <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-3 border-t border-border text-xs text-muted-foreground">
            <div className="flex items-center gap-2">
              <span>Rows per page</span>
              <select
                value={String(pageSize)}
                onChange={(e) => setPageSize(Number(e.target.value))}
                className="h-8 rounded-md border border-border bg-card px-2 pr-6 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary/40"
              >
                {PAGE_SIZE_OPTIONS.map((opt) => (<option key={opt} value={opt}>{opt}</option>))}
              </select>
            </div>
            <span className="text-center">{startIndex}–{endIndex} of {totalCount}</span>
            <div className="flex items-center gap-1">
              <button onClick={() => setCurrentPage(1)} disabled={currentPage === 1} className="p-1.5 rounded-md hover:bg-muted disabled:opacity-40 disabled:cursor-not-allowed"><ChevronsLeft className="w-4 h-4" /></button>
              <button onClick={() => setCurrentPage((p) => Math.max(1, p - 1))} disabled={currentPage === 1} className="p-1.5 rounded-md hover:bg-muted disabled:opacity-40 disabled:cursor-not-allowed"><ChevronLeft className="w-4 h-4" /></button>
              <button onClick={() => setCurrentPage((p) => Math.min(pageCount, p + 1))} disabled={currentPage >= pageCount} className="p-1.5 rounded-md hover:bg-muted disabled:opacity-40 disabled:cursor-not-allowed"><ChevronRight className="w-4 h-4" /></button>
              <button onClick={() => setCurrentPage(pageCount)} disabled={currentPage >= pageCount} className="p-1.5 rounded-md hover:bg-muted disabled:opacity-40 disabled:cursor-not-allowed"><ChevronsRight className="w-4 h-4" /></button>
            </div>
          </div>
        )}
      </div>

      {/* Mobile pagination */}
      {totalCount > 0 && (
        <div className="sm:hidden mt-4 flex items-center justify-between gap-2 text-sm text-muted-foreground">
          <span>{startIndex}–{endIndex} of {totalCount}</span>
          <div className="flex items-center gap-1">
            <button onClick={() => setCurrentPage((p) => Math.max(1, p - 1))} disabled={currentPage === 1} className="p-2 rounded-lg bg-card border border-border disabled:opacity-40 disabled:cursor-not-allowed"><ChevronLeft className="w-4 h-4" /></button>
            <span className="px-3 py-1 rounded-lg bg-card border border-border text-xs font-medium">{currentPage} / {pageCount}</span>
            <button onClick={() => setCurrentPage((p) => Math.min(pageCount, p + 1))} disabled={currentPage >= pageCount} className="p-2 rounded-lg bg-card border border-border disabled:opacity-40 disabled:cursor-not-allowed"><ChevronRight className="w-4 h-4" /></button>
          </div>
        </div>
      )}
    </div>
  );
}
