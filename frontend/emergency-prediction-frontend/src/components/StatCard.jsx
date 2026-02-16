import { motion } from "framer-motion";

export default function StatCard({ title, value, subtext, icon: Icon, trend }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-sm border border-gray-100 dark:border-slate-700 hover:shadow-md transition-shadow"
        >
            <div className="flex justify-between items-start">
                <div>
                    <p className="text-sm font-medium text-gray-500 dark:text-slate-400 uppercase tracking-wider">
                        {title}
                    </p>
                    <h3 className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                        {value}
                    </h3>
                </div>
                <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded-xl">
                    <Icon className="w-6 h-6 text-red-600 dark:text-red-400" />
                </div>
            </div>

            {subtext && (
                <div className="mt-4 flex items-center text-sm">
                    {trend && (
                        <span className={`font-medium ${trend > 0 ? 'text-emerald-500' : 'text-red-500'}`}>
                            {trend > 0 ? '+' : ''}{trend}%
                        </span>
                    )}
                    <span className="text-gray-500 dark:text-slate-400 ml-2">
                        {subtext}
                    </span>
                </div>
            )}
        </motion.div>
    );
}
