import { motion } from "framer-motion";

const incidents = [
    {
        id: "INC-1001",
        type: "Fire",
        location: "Main St & 5th Ave",
        severity: "Critical",
        confidence: "94%",
        status: "Dispatched",
    },
    {
        id: "INC-1002",
        type: "Medical",
        location: "Oak Park, Zone B",
        severity: "High",
        confidence: "87%",
        status: "Active",
    },
    {
        id: "INC-1003",
        type: "Traffic",
        location: "Highway 101, Mile 34",
        severity: "Medium",
        confidence: "78%",
        status: "Dispatched",
    },
    {
        id: "INC-1004",
        type: "Rescue",
        location: "Riverside Trail",
        severity: "Low",
        confidence: "91%",
        status: "Resolved",
    },
    {
        id: "INC-1005",
        type: "Fire",
        location: "Industrial Park E",
        severity: "High",
        confidence: "82%",
        status: "Dispatched",
    },
];

const SeverityBadge = ({ severity }) => {
    let styles = "";

    switch (severity.toLowerCase()) {
        case "critical":
            styles = "bg-destructive/10 text-destructive border border-destructive/20";
            break;
        case "high":
            styles = "bg-orange-500/10 text-orange-600 dark:text-orange-400 border border-orange-500/20";
            break;
        case "medium":
            styles = "bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20";
            break;
        case "low":
            styles = "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20";
            break;
        default:
            styles = "bg-muted text-muted-foreground border border-border";
    }

    return (
        <span className={`px-2.5 py-1 rounded-md text-xs font-semibold uppercase tracking-wider flex items-center gap-1.5 w-fit transition-colors ${styles}`}>
            <span className="w-1.5 h-1.5 rounded-full bg-current"></span>
            {severity}
        </span>
    );
};

export default function RecentIncidents({ incidents: propIncidents, loading }) {
    const displayIncidents = propIncidents && propIncidents.length > 0 ? propIncidents : incidents;

    if (loading) {
        return (
            <div className="bg-card p-6 rounded-2xl shadow-sm border border-border mt-8 animate-pulse">
                <div className="h-6 w-48 bg-muted rounded mb-6"></div>
                <div className="space-y-4">
                    {[1, 2, 3, 4, 5].map((i) => (
                        <div key={i} className="h-12 bg-muted rounded"></div>
                    ))}
                </div>
            </div>
        );
    }

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.4 }}
            className="bg-card p-4 sm:p-6 rounded-2xl shadow-sm border border-border mt-6 sm:mt-8"
        >
            <h3 className="text-base sm:text-lg font-bold text-foreground mb-4 sm:mb-6">
                Recent Incidents
            </h3>

            <div className="overflow-x-auto -mx-4 sm:mx-0">
                <div className="inline-block min-w-full align-middle">
                    <table className="min-w-full">
                        <thead>
                            <tr className="border-b border-border text-left">
                                <th className="pb-3 sm:pb-4 pl-4 sm:pl-2 text-xs font-bold text-muted-foreground uppercase tracking-wider whitespace-nowrap">ID</th>
                                <th className="pb-3 sm:pb-4 px-2 text-xs font-bold text-muted-foreground uppercase tracking-wider whitespace-nowrap">Type</th>
                                <th className="pb-3 sm:pb-4 px-2 text-xs font-bold text-muted-foreground uppercase tracking-wider whitespace-nowrap">Location</th>
                                <th className="pb-3 sm:pb-4 px-2 text-xs font-bold text-muted-foreground uppercase tracking-wider whitespace-nowrap">Severity</th>
                                <th className="pb-3 sm:pb-4 px-2 text-xs font-bold text-muted-foreground uppercase tracking-wider whitespace-nowrap">Confidence</th>
                                <th className="pb-3 sm:pb-4 pr-4 sm:pr-2 text-xs font-bold text-muted-foreground uppercase tracking-wider whitespace-nowrap">Status</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-border">
                            {displayIncidents.map((incident) => {
                                const displayId = typeof incident.id === 'number' ? `INC-${incident.id}` : incident.id;
                                return (
                                    <tr key={incident.id} className="group hover:bg-muted/30 transition-colors">
                                        <td className="py-3 sm:py-4 pl-4 sm:pl-2 text-xs sm:text-sm font-medium text-primary cursor-pointer hover:underline hover:text-red-700 transition-colors whitespace-nowrap">
                                            {displayId}
                                        </td>
                                        <td className="py-3 sm:py-4 px-2 text-xs sm:text-sm text-foreground font-medium whitespace-nowrap">
                                            {incident.type}
                                        </td>
                                        <td className="py-3 sm:py-4 px-2 text-xs sm:text-sm text-muted-foreground whitespace-nowrap">
                                            {incident.location || incident.twp || "Unknown"}
                                        </td>
                                        <td className="py-3 sm:py-4 px-2 whitespace-nowrap">
                                        <SeverityBadge severity={incident.severity || "Low"} />
                                    </td>
                                        <td className="py-3 sm:py-4 px-2 text-xs sm:text-sm text-foreground font-semibold whitespace-nowrap">
                                            {incident.confidence || "N/A"}
                                        </td>
                                        <td className="py-3 sm:py-4 pr-4 sm:pr-2 text-xs sm:text-sm text-muted-foreground whitespace-nowrap">
                                            {incident.status || "Resolved"}
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            </div>
        </motion.div>
    );
}
