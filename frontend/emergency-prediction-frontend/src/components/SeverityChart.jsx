import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { motion } from 'framer-motion';

const defaultData = [
    { day: 'Tue', low: 12, medium: 18, high: 3, critical: 5 },
    { day: 'Wed', low: 16, medium: 16, high: 5, critical: 1 },
    { day: 'Thu', low: 11, medium: 10, high: 6, critical: 3 },
    { day: 'Fri', low: 6, medium: 8, high: 8, critical: 2 },
    { day: 'Sat', low: 23, medium: 8, high: 6, critical: 2 },
    { day: 'Sun', low: 19, medium: 15, high: 11, critical: 2 },
    { day: 'Mon', low: 9, medium: 9, high: 12, critical: 1 },
];

export default function SeverityChart({ data = defaultData }) {
    const chartData = data && data.length > 0 ? data : defaultData;
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.3 }}
            className="bg-card p-6 rounded-xl border border-border mt-8"
        >
            <h3 className="text-lg font-bold text-foreground mb-6">
                Severity Trend (7 Days)
            </h3>
            <div className="h-52 sm:h-72 w-full">
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                        data={chartData}
                        margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                    >
                        <CartesianGrid
                            strokeDasharray="3 3"
                            vertical={false}
                            stroke="hsl(var(--border))"
                            opacity={0.5}
                        />
                        <XAxis
                            dataKey="day"
                            axisLine={false}
                            tickLine={false}
                            tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
                            dy={10}
                        />
                        <YAxis
                            axisLine={false}
                            tickLine={false}
                            tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
                        />
                        <Tooltip
                            cursor={{ fill: 'hsl(var(--muted))', opacity: 0.2 }}
                            contentStyle={{
                                backgroundColor: 'hsl(var(--card))',
                                borderRadius: '8px',
                                border: '1px solid hsl(var(--border))',
                                boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                                color: 'hsl(var(--card-foreground))'
                            }}
                            itemStyle={{ fontSize: 13, fontWeight: 500 }}
                            labelStyle={{ color: 'hsl(var(--muted-foreground))', marginBottom: '0.5rem' }}
                        />
                        <Legend
                            iconType="circle"
                            verticalAlign="top"
                            align="right"
                            wrapperStyle={{ paddingBottom: '20px' }}
                            formatter={(value) => <span className="text-muted-foreground text-sm font-medium ml-1 capitalize">{value}</span>}
                        />
                        <Bar dataKey="low" name="Low" fill="#22c55e" radius={[4, 4, 0, 0]} maxBarSize={40} />
                        <Bar dataKey="medium" name="Medium" fill="#f97316" radius={[4, 4, 0, 0]} maxBarSize={40} />
                        <Bar dataKey="high" name="High" fill="#ea580c" radius={[4, 4, 0, 0]} maxBarSize={40} />
                        <Bar dataKey="critical" name="Critical" fill="#ef4444" radius={[4, 4, 0, 0]} maxBarSize={40} />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </motion.div>
    );
}
