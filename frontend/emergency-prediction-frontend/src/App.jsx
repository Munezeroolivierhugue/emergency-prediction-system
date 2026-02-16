import Sidebar from "./components/Sidebar";
import AppRoutes from "./routes/AppRoutes";

function App() {
  return (
    <div className="flex h-screen bg-gray-50 dark:bg-slate-950 transition-colors duration-300">
      <Sidebar />
      <div className="flex-1 flex flex-col ml-64 transition-all duration-300">
        <main className="flex-1 p-8 overflow-y-auto bg-background">
          <AppRoutes />
        </main>
      </div>
    </div>
  );
}

export default App;