import { motion } from "framer-motion";

export default function StatCard({ title, value, subtext, icon: Icon, trend }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="relative overflow-hidden before:absolute before:top-0 before:left-0 before:w-full before:h-[2px] before:bg-gradient-to-r before:from-transparent before:via-primary before:to-transparent before:content-[''] bg-card p-3 sm:p-5 rounded-2xl shadow-sm border border-border hover:shadow-md transition-shadow"
        >
            <div className="flex justify-between items-start">
                <div className="flex-1 min-w-0 pr-2">
                    <p className="text-[10px] sm:text-xs font-semibold text-muted-foreground uppercase tracking-wider leading-tight">
                        {title}
                    </p>
                    <h3 className="text-xl sm:text-3xl font-bold text-foreground mt-1 sm:mt-2 truncate">
                        {value}
                    </h3>
                </div>
                <div className="p-1.5 sm:p-3 bg-primary/10 rounded-xl shrink-0">
                    <Icon className="w-4 h-4 sm:w-6 sm:h-6 text-primary" />
                </div>
            </div>

            {subtext && (
                <div className="mt-2 sm:mt-4 flex items-center text-[11px] sm:text-sm flex-wrap gap-x-1">
                    {trend && (
                        <span className={`font-semibold ${trend > 0 ? 'text-emerald-500' : 'text-destructive'}`}>
                            {trend > 0 ? '+' : ''}{trend}%
                        </span>
                    )}
                    <span className="text-muted-foreground">
                        {subtext}
                    </span>
                </div>
            )}
        </motion.div>
    );
}
