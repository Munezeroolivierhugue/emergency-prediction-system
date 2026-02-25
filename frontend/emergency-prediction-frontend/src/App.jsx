import Sidebar from "./components/Sidebar";
import AppRoutes from "./routes/AppRoutes";
import { Toaster } from "react-hot-toast";
import { useLocation } from "react-router-dom";

function App() {
  const location = useLocation();
  const isAuthPage = ["/login", "/register"].includes(location.pathname);

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-neutral-950 transition-colors duration-300">
      <Toaster position="top-right" />
      {!isAuthPage && <Sidebar />}
      <div className={`flex-1 flex flex-col transition-all duration-300 ${!isAuthPage ? "ml-64" : ""}`}>
        <main className={`flex-1 overflow-y-auto bg-background ${!isAuthPage ? "p-8" : ""}`}>
          <AppRoutes />
        </main>
      </div>
    </div>
  );
}

export default App;
