export const DUMMY_STATS = {
    total_incidents: 2045,
    critical_count: 12,
    by_type: [
        { name: "Fire", value: 520, color: "#ef4444" },
        { name: "EMS", value: 980, color: "#b91c1c" },
        { name: "Traffic", value: 545, color: "#f97316" }
    ]
};

export const DUMMY_SEVERITY_DATA = [
    { day: "Feb 18", critical: 1, high: 3, medium: 8, low: 15 },
    { day: "Feb 19", critical: 2, high: 5, medium: 10, low: 12 },
    { day: "Feb 20", critical: 0, high: 4, medium: 12, low: 18 },
    { day: "Feb 21", critical: 3, high: 6, medium: 7, low: 11 },
    { day: "Feb 22", critical: 1, high: 2, medium: 9, low: 20 },
    { day: "Feb 23", critical: 4, high: 8, medium: 5, low: 14 },
    { day: "Feb 24", critical: 2, high: 5, medium: 11, low: 16 }
];

export const DUMMY_HOURLY_DATA = Array.from({ length: 24 }, (_, i) => ({
    time: `${String(i).padStart(2, '0')}:00`,
    calls: Math.floor(Math.random() * 15) + 5
}));

export const DUMMY_INCIDENTS = [
    { id: 1001, type: "Fire", twp: "Main St & 5th Ave", timestamp: new Date().toISOString(), severity: "Critical", confidence: 0.94, status: "Dispatched" },
    { id: 1002, type: "EMS", twp: "Oak Rd", timestamp: new Date().toISOString(), severity: "High", confidence: 0.88, status: "Responding" },
    { id: 1003, type: "Traffic", twp: "Route 202", timestamp: new Date().toISOString(), severity: "Medium", confidence: 0.75, status: "Resolved" },
    { id: 1004, type: "EMS", twp: "Cedar Ln", timestamp: new Date().toISOString(), severity: "Low", confidence: 0.91, status: "Resolved" },
    { id: 1005, type: "Fire", twp: "Highland Blvd", timestamp: new Date().toISOString(), severity: "High", confidence: 0.82, status: "Dispatched" }
];

export const DUMMY_PREDICTION = {
    severity: "High",
    confidence: 0.85,
    recommended_response: "Dispatch 2 Units (Demo Mode)"
};
