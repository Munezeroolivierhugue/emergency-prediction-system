import { Routes, Route } from "react-router-dom";
import Dashboard from "../pages/Dashboard";
import Newincident from "../components/Newincident";
import History from "../pages/History";
import Settings from "../pages/Settings";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/newincident" element={<Newincident />} />
      <Route path="/history" element={<History />} />
      <Route path="/settings" element={<Settings />} />
    </Routes>
  );
}
