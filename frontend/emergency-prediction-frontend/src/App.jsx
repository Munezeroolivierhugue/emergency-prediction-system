import { useState } from "react";
import Sidebar from "./components/Sidebar";
import AppRoutes from "./routes/AppRoutes";
import { Toaster } from "react-hot-toast";
import { useLocation } from "react-router-dom";
import { Menu } from "lucide-react";

function App() {
  const location = useLocation();
  const isAuthPage = ["/login", "/register"].includes(location.pathname);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen overflow-hidden bg-background transition-colors duration-300">
      <Toaster position="top-right" />
      {!isAuthPage && <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />}
      <div className={`flex-1 flex flex-col min-w-0 transition-all duration-300 ${!isAuthPage ? "lg:ml-64" : ""}`}>
        {!isAuthPage && (
          <div className="lg:hidden flex items-center justify-between p-4 bg-background border-b border-border">
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-800 transition-colors"
            >
              <Menu className="w-6 h-6 text-gray-600 dark:text-slate-400" />
            </button>
            <h1 className="text-lg font-bold bg-gradient-to-r from-red-600 to-red-500 bg-clip-text text-transparent">
              Emergency
            </h1>
          </div>
        )}
        <main className={`flex-1 overflow-y-auto overflow-x-hidden bg-background ${!isAuthPage ? "p-3 sm:p-6 lg:p-8" : ""}`}>
          <AppRoutes />
        </main>
      </div>
    </div>
  );
}

export default App;
