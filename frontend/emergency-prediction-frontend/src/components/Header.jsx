import { Link } from "react-router-dom";
import ThemeToggle from "./ThemeToggle";

export default function Header() {
  return (
    <header className="fixed top-0 left-0 w-full z-50 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md shadow-sm border-b border-gray-100 dark:border-slate-800 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex-shrink-0 flex items-center">
            <Link to="/" className="text-2xl font-bold bg-gradient-to-r from-red-600 to-red-500 bg-clip-text text-transparent hover:opacity-80 transition-opacity">
              EmergencyResponse
            </Link>
          </div>

          <nav className="flex items-center space-x-4">
            {/* Placeholder for future nav links */}
            <ThemeToggle />
          </nav>
        </div>
      </div>
    </header>
  );
}
