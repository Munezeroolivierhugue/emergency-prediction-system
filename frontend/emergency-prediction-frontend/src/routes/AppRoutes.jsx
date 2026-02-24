import { Routes, Route } from "react-router-dom";
import Dashboard from "../pages/Dashboard";
import Newincident from "../components/Newincident";
import History from "../pages/History";
<<<<<<< HEAD
import Settings from "../components/Settings";
import Login from "../pages/Login";
import Register from "../pages/Register";
=======
import Settings from "../pages/Settings";
>>>>>>> 3fbe8be6c4772ed9257574dbaba09bbef4d12f20

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/newincident" element={<Newincident />} />
      <Route path="/history" element={<History />} />
      <Route path="/settings" element={<Settings />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
    </Routes>
  );
}
