import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { motion } from 'framer-motion';

const defaultData = [
    { name: 'Fire', value: 35, color: '#ef4444' },
    { name: 'EMS', value: 45, color: '#dc2626' },
    { name: 'Traffic', value: 15, color: '#f97316' },
];

export default function IncidentChart({ data = defaultData, total }) {
    const chartData = data && data.length > 0 ? data : defaultData;
    const totalValue = total || chartData.reduce((acc, curr) => acc + curr.value, 0);

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.2 }}
            className="bg-card p-6 rounded-2xl shadow-sm border border-border"
        >
            <h3 className="text-lg font-bold text-foreground mb-4">
                Incident Types
            </h3>
            <div className="h-80 w-full relative">
                <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                        <Pie
                            data={chartData}
                            innerRadius={80}
                            outerRadius={100}
                            paddingAngle={5}
                            dataKey="value"
                        >
                            {chartData.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={entry.color} strokeWidth={0} />
                            ))}
                        </Pie>
                        <Tooltip
                            contentStyle={{
                                backgroundColor: 'hsl(var(--card))',
                                borderRadius: '8px',
                                border: '1px solid hsl(var(--border))',
                                boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                                color: 'hsl(var(--card-foreground))'
                            }}
                            itemStyle={{ color: 'hsl(var(--card-foreground))' }}
                        />
                        <Legend
                            verticalAlign="bottom"
                            height={36}
                            iconType="square"
                            formatter={(value) => <span className="text-muted-foreground ml-1">{value}</span>}
                        />
                    </PieChart>
                </ResponsiveContainer>

                {/* Center Text */}
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none pb-8">
                    <span className="text-3xl font-bold text-foreground">
                        {totalValue.toLocaleString()}
                    </span>
                    <span className="text-xs text-muted-foreground uppercase tracking-wide">
                        Total
                    </span>
                </div>
            </div>
        </motion.div>
    );
}
