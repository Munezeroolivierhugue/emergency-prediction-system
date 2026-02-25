import { motion } from "framer-motion";

export default function StatCard({ title, value, subtext, icon: Icon, trend }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="bg-card p-6 rounded-xl border border-border shadow-sm hover:border-primary/20 transition-colors"
        >
            <div className="flex justify-between items-start">
                <div>
                    <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                        {title}
                    </p>
                    <h3 className="text-2xl font-bold text-foreground mt-2">
                        {value}
                    </h3>
                </div>
                <div className="p-2.5 bg-primary/10 rounded-lg">
                    <Icon className="w-5 h-5 text-primary" />
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
