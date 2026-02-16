import { motion } from "framer-motion";

export default function StatCard({ title, value, subtext, icon: Icon, trend }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="relative overflow-hidden before:absolute before:top-0 before:left-0 before:w-full before:h-[2px] before:bg-gradient-to-r before:from-transparent before:via-primary before:to-transparent before:content-[''] bg-card p-6 rounded-2xl shadow-sm border border-border hover:shadow-md transition-shadow"
        >
            <div className="flex justify-between items-start">
                <div>
                    <p className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
                        {title}
                    </p>
                    <h3 className="text-3xl font-bold text-foreground mt-2">
                        {value}
                    </h3>
                </div>
                <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded-xl">
                    <Icon className="w-6 h-6 text-primary" />
                </div>
            </div>

            {subtext && (
                <div className="mt-4 flex items-center text-sm">
                    {trend && (
                        <span className={`font-medium ${trend > 0 ? 'text-emerald-500' : 'text-destructive'}`}>
                            {trend > 0 ? '+' : ''}{trend}%
                        </span>
                    )}
                    <span className="text-muted-foreground ml-2">
                        {subtext}
                    </span>
                </div>
            )}
        </motion.div>
    );
}
