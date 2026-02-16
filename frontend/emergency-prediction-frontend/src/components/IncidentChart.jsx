import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { motion } from 'framer-motion';

const data = [
    { name: 'Fire', value: 35, color: '#EF4444' },    // Red-500
    { name: 'Medical', value: 45, color: '#3B82F6' }, // Blue-500
    { name: 'Traffic', value: 15, color: '#F97316' }, // Orange-500
    { name: 'Rescue', value: 20, color: '#10B981' },  // Emerald-500
];

export default function IncidentChart() {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.2 }}
            className="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-sm border border-gray-100 dark:border-slate-700"
        >
            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
                Incident Types
            </h3>
            <div className="h-80 w-full relative">
                <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                        <Pie
                            data={data}
                            innerRadius={80}
                            outerRadius={100}
                            paddingAngle={5}
                            dataKey="value"
                        >
                            {data.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={entry.color} strokeWidth={0} />
                            ))}
                        </Pie>
                        <Tooltip
                            contentStyle={{
                                backgroundColor: '#fff',
                                borderRadius: '8px',
                                border: 'none',
                                boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                            }}
                        />
                        <Legend
                            verticalAlign="bottom"
                            height={36}
                            iconType="square"
                            formatter={(value) => <span className="text-gray-600 dark:text-slate-300 ml-1">{value}</span>}
                        />
                    </PieChart>
                </ResponsiveContainer>

                {/* Center Text */}
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none pb-8">
                    <span className="text-3xl font-bold text-gray-900 dark:text-white">
                        1,245
                    </span>
                    <span className="text-xs text-gray-500 dark:text-slate-400 uppercase tracking-wide">
                        Total
                    </span>
                </div>
            </div>
        </motion.div>
    );
}
