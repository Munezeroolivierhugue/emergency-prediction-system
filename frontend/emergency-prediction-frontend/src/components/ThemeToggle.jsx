import { Sun, Moon } from "lucide-react";
import { useTheme } from "../context/ThemeContext";

export default function ThemeToggle() {
  const { dark, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="p-2 rounded-full bg-gray-200 dark:bg-neutral-700 hover:bg-gray-300 dark:hover:bg-neutral-600 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-neutral-400"
      aria-label="Toggle Theme"
    >
      {dark ? (
        <Sun className="text-yellow-400" size={20} />
      ) : (
        <Moon className="text-neutral-800 dark:text-neutral-200" size={20} />
      )}
    </button>
  );
}
