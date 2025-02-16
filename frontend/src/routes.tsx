import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Login from "./pages/Login";
import ProtectedRoute from "./components/ProtectedRoute";

const AppRoutes = () => (
    <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        {/* Protect future routes */}
        <Route
            path="/dashboard"
            element={
                <ProtectedRoute>
                    <h2>Dashboard (Protected)</h2>
                </ProtectedRoute>
            }
        />
    </Routes>
);

export default AppRoutes;
