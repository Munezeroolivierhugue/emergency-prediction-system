import { Sun, Moon } from "lucide-react";
import { useTheme } from "../context/ThemeContext";

export default function ThemeToggle() {
  const { dark, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="p-2 rounded-full bg-gray-200 dark:bg-slate-700 hover:bg-gray-300 dark:hover:bg-slate-600 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-slate-400"
      aria-label="Toggle Theme"
    >
      {dark ? (
        <Sun className="text-yellow-400" size={20} />
      ) : (
        <Moon className="text-slate-800 dark:text-slate-200" size={20} />
      )}
    </button>
  );
}
