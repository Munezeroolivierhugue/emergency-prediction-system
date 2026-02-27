import { Link, useLocation, useNavigate } from "react-router-dom";
import {
    LayoutDashboard,
    PlusCircle,
    History,
    Settings,
    LogOut,
    Sun,
    Moon
} from "lucide-react";
import { useTheme } from "../context/ThemeContext";
import toast from "react-hot-toast";

export default function Sidebar() {
    const { dark, toggleTheme } = useTheme();
    const location = useLocation();
    const navigate = useNavigate();

    const isActive = (path) => location.pathname === path;

    const navItems = [
        { icon: LayoutDashboard, label: "Dashboard", path: "/" },
        { icon: PlusCircle, label: "New Incident", path: "/newincident" },
        { icon: History, label: "History", path: "/history" },
        { icon: Settings, label: "Settings", path: "/settings" },
    ];

    const handleLogout = () => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        toast.success("Logged out successfully");
        navigate("/login");
    };

    return (
        <aside className="fixed left-0 top-0 h-screen w-64 bg-background border-r border-border flex flex-col transition-colors duration-300 z-50">
            {/* Header / Logo */}
            <div className="p-6">
                <div className="flex items-center space-x-2">
                    <div className="bg-primary/10 p-2 rounded-lg">
                        <svg
                            className="w-6 h-6 text-primary"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                            xmlns="http://www.w3.org/2000/svg"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                            />
                        </svg>
                    </div>
                    <div>
                        <h1 className="text-lg font-bold text-foreground">
                            Emergency
                        </h1>
                        <p className="text-[10px] text-muted-foreground tracking-wider uppercase font-medium">
                            Prediction System
                        </p>
                    </div>
                </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 px-4 py-4 space-y-2">
                {navItems.map((item) => {
                    const Icon = item.icon;
                    const active = isActive(item.path);

                    return (
                        <Link
                            key={item.path}
                            to={item.path}
                            className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors duration-200 group ${active
                                ? "bg-primary text-primary-foreground font-medium"
                                : "text-muted-foreground hover:bg-muted hover:text-foreground"
                                }`}
                        >
                            <Icon size={20} className={active ? "text-primary-foreground" : "text-muted-foreground group-hover:text-foreground"} />
                            <span>{item.label}</span>
                        </Link>
                    )
                })}
            </nav>

            {/* Footer Actions */}
            <div className="p-4 border-t border-border space-y-4">

                {/* Theme Toggle */}
                <button
                    onClick={toggleTheme}
                    className="flex items-center space-x-3 px-4 py-2 w-full text-left rounded-lg text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
                >
                    {dark ? <Sun size={20} /> : <Moon size={20} />}
                    <span>{dark ? "Light Mode" : "Dark Mode"}</span>
                </button>

                {/* User Profile */}
                <div className="flex items-center space-x-3 px-4 py-2">
                    <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold text-sm">
                        D1
                    </div>
                    <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-foreground truncate">
                            Dispatcher 1
                        </p>
                        <p className="text-xs text-muted-foreground truncate">
                            On Shift
                        </p>
                    </div>
                </div>

                {/* Logout */}
                <button
                    onClick={handleLogout}
                    className="flex items-center space-x-3 px-4 py-2 w-full text-left text-muted-foreground hover:text-destructive transition-colors"
                >
                    <LogOut size={18} />
                    <span className="text-sm">Logout</span>
                </button>

            </div>
        </aside>
    );
}
