import { Activity, AlertTriangle, Truck, Users, Flame } from "lucide-react";
import StatCard from "../components/StatCard";
import TrafficChart from "../components/TrafficChart";
import SeverityChart from "../components/SeverityChart";
import IncidentChart from "../components/IncidentChart";
import RecentIncidents from "../components/RecentIncidents";

export default function Dashboard() {
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
          value="1,245"
          subtext="from last week"
          trend={12}
          icon={Activity}
        />
        <StatCard
          title="Critical Alerts"
          value="5"
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
          <TrafficChart />
        </div>
        <div className="lg:col-span-1">
          <IncidentChart />
        </div>
      </div>

      {/* Severity Trend Section */}
      <div className="w-full mb-8">
        <SeverityChart />
      </div>

      {/* Recent Incidents Section */}
      <div className="w-full">
        <RecentIncidents />
      </div>
    </div>
  );
}
