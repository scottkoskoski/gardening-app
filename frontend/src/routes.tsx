import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ProtectedRoute from "./components/ProtectedRoute";
import Profile from "./pages/Profile";
import GardenView from "./pages/GardenView";

const AppRoutes = () => (
    <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
            path="/profile"
            element={
                <ProtectedRoute>
                    <Profile />
                </ProtectedRoute>
            }
        />
        <Route
            path="/gardens"
            element={
                <ProtectedRoute>
                    <GardenView />
                </ProtectedRoute>
            }
        />
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
