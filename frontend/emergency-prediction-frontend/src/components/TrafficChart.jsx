import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
} from "recharts";
import { motion } from "framer-motion";

const data = [
    { time: "00:00", calls: 45 },
    { time: "01:00", calls: 12 },
    { time: "02:00", calls: 48 },
    { time: "03:00", calls: 19 },
    { time: "04:00", calls: 30 },
    { time: "05:00", calls: 35 },
    { time: "06:00", calls: 14 },
    { time: "07:00", calls: 40 },
    { time: "08:00", calls: 25 },
    { time: "09:00", calls: 12 },
    { time: "10:00", calls: 20 },
    { time: "11:00", calls: 35 },
    { time: "12:00", calls: 48 },
    { time: "13:00", calls: 19 },
    { time: "14:00", calls: 25 },
    { time: "15:00", calls: 47 },
    { time: "16:00", calls: 25 },
    { time: "17:00", calls: 13 },
    { time: "18:00", calls: 13 },
    { time: "19:00", calls: 45 },
    { time: "20:00", calls: 25 },
    { time: "21:00", calls: 22 },
    { time: "22:00", calls: 43 },
    { time: "23:00", calls: 35 },
];

export default function TrafficChart() {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.1 }}
            className="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-sm border border-gray-100 dark:border-slate-700"
        >
            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-6">
                Incoming Calls (24h)
            </h3>
            <div className="h-80 w-full">
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart
                        data={data}
                        margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
                    >
                        <defs>
                            <linearGradient id="colorCalls" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#DC2626" stopOpacity={0.1} />
                                <stop offset="95%" stopColor="#DC2626" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid
                            strokeDasharray="3 3"
                            vertical={true}
                            stroke="#E2E8F0"
                            className="dark:stroke-slate-700"
                        />
                        <XAxis
                            dataKey="time"
                            axisLine={false}
                            tickLine={false}
                            tick={{ fill: "#94A3B8", fontSize: 12 }}
                            interval={2}
                        />
                        <YAxis
                            axisLine={false}
                            tickLine={false}
                            tick={{ fill: "#94A3B8", fontSize: 12 }}
                        />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: "#fff",
                                borderRadius: "8px",
                                border: "none",
                                boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                            }}
                            itemStyle={{ color: "#DC2626" }}
                        />
                        <Area
                            type="monotone"
                            dataKey="calls"
                            stroke="#DC2626"
                            strokeWidth={2}
                            fillOpacity={1}
                            fill="url(#colorCalls)"
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </motion.div>
    );
}
