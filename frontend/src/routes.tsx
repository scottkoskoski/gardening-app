import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import PlantDetail from "./pages/PlantDetail";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ProtectedRoute from "./components/ProtectedRoute";
import Profile from "./pages/Profile";
import GardenView from "./pages/GardenView";
import Dashboard from "./pages/Dashboard";
import GardenMap from "./pages/GardenMap";
import GardenJournal from "./pages/GardenJournal";

const AppRoutes = () => (
    <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/plants/:plantId" element={<PlantDetail />} />
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
        <Route
            path="/gardens/:gardenId/map"
            element={
                <ProtectedRoute>
                    <GardenMap />
                </ProtectedRoute>
            }
        />
        <Route
            path="/gardens/:gardenId/journal"
            element={
                <ProtectedRoute>
                    <GardenJournal />
                </ProtectedRoute>
            }
        />
        <Route
            path="/dashboard"
            element={
                <ProtectedRoute>
                    <Dashboard />
                </ProtectedRoute>
            }
        />
    </Routes>
);

export default AppRoutes;
