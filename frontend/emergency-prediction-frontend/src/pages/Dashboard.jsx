import React, { useState, useEffect } from "react";
import { Activity, AlertTriangle, Truck, Users, Flame } from "lucide-react";
import StatCard from "../components/StatCard";
import TrafficChart from "../components/TrafficChart";
import SeverityChart from "../components/SeverityChart";
import IncidentChart from "../components/IncidentChart";
import RecentIncidents from "../components/RecentIncidents";
import { analyticsService, incidentService } from "../utils/api";
import { DUMMY_STATS, DUMMY_SEVERITY_DATA, DUMMY_HOURLY_DATA, DUMMY_INCIDENTS } from "../utils/dummyData";

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [severityData, setSeverityData] = useState([]);
  const [hourlyData, setHourlyData] = useState([]);
  const [recentIncidents, setRecentIncidents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, severityRes, hourlyRes, incidentsRes] = await Promise.all([
          analyticsService.getStatistics().catch(() => ({ data: DUMMY_STATS })),
          analyticsService.getSeverityByDay().catch(() => ({ data: DUMMY_SEVERITY_DATA })),
          analyticsService.getHourlyCalls().catch(() => ({ data: DUMMY_HOURLY_DATA })),
          incidentService.getIncidents({ limit: 5 }).catch(() => ({ data: { results: DUMMY_INCIDENTS } })),
        ]);

        // Normalize Statistics Data
        let normalizedStats = statsRes.data || DUMMY_STATS;
        if (normalizedStats.by_type && !Array.isArray(normalizedStats.by_type)) {
          // Convert dict to expected array format
          const typeColors = { "EMS": "#dc2626", "Fire": "#ef4444", "Traffic": "#f97316" };
          normalizedStats.by_type = Object.entries(normalizedStats.by_type).map(([key, value]) => ({
            name: key,
            value: value,
            color: typeColors[key] || "#cbd5e1"
          }));
        }
        if (!normalizedStats.total_incidents && normalizedStats.by_type) {
          normalizedStats.total_incidents = normalizedStats.by_type.reduce((acc, curr) => acc + (curr.value || 0), 0);
        }

        // Normalize Hourly Data
        let normalizedHourly = hourlyRes.data || DUMMY_HOURLY_DATA;
        if (Array.isArray(normalizedHourly) && normalizedHourly.length > 0) {
          // Handle cases where keys might be 'hour'/'count' instead of 'time'/'calls'
          normalizedHourly = normalizedHourly.map(item => ({
            time: item.time || item.hour || "00:00",
            calls: typeof item.calls === 'number' ? item.calls : (item.count || 0)
          }));
        }

        // Normalize Severity Data
        let normalizedSeverity = severityRes.data || DUMMY_SEVERITY_DATA;
        if (Array.isArray(normalizedSeverity) && normalizedSeverity.length > 0) {
          normalizedSeverity = normalizedSeverity.map(item => ({
            ...item,
            day: item.day || item.date || "N/A"
          }));
        }

        setStats(normalizedStats);
        setSeverityData(normalizedSeverity);
        setHourlyData(normalizedHourly);
        setRecentIncidents(incidentsRes.data.results || DUMMY_INCIDENTS);
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="min-h-screen bg-background text-foreground p-6 lg:p-8 transition-colors duration-300">

      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-foreground">
            Command Center
          </h1>
          <p className="text-muted-foreground mt-1">
            Real-time emergency monitoring overview
          </p>
        </div>
        <div className="mt-4 md:mt-0">
          <button className="bg-red-600 hover:bg-red-700 text-white px-6 py-2.5 rounded-xl font-medium shadow-lg shadow-red-600/30 transition-all active:scale-95 flex items-center gap-2 cursor-pointer">
            <AlertTriangle className="w-5 h-5" />
            Trigger Emergency Alert
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Total Incidents"
          value={stats?.total_incidents?.toLocaleString() || (loading ? "..." : "1,245")}
          subtext="from last week"
          trend={12}
          icon={Activity}
        />
        <StatCard
          title="Critical Alerts"
          value={stats?.critical_count?.toString() || (loading ? "..." : "5")}
          subtext="Active today"
          icon={AlertTriangle}
        />
        <StatCard
          title="Active Dispatches"
          value="18"
          subtext="Currently deployed"
          icon={Flame}
        />
        <StatCard
          title="Units Available"
          value="42"
          subtext="Out of 60 total"
          icon={Users}
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
        <div className="lg:col-span-2">
          <TrafficChart data={hourlyData} />
        </div>
        <div className="lg:col-span-1">
          <IncidentChart data={stats?.by_type} total={stats?.total_incidents} />
        </div>
      </div>

      {/* Severity Trend Section */}
      <div className="w-full mb-8">
        <SeverityChart data={severityData} />
      </div>

      {/* Recent Incidents Section */}
      <div className="w-full">
        <RecentIncidents incidents={recentIncidents} loading={loading} />
      </div>
    </div>
  );
}
