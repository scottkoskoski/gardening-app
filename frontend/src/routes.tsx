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
import PlantingCalendar from "./pages/PlantingCalendar";
import Recommendations from "./pages/Recommendations";
import Tasks from "./pages/Tasks";
import HarvestLog from "./pages/HarvestLog";
import HarvestSummary from "./pages/HarvestSummary";
import SoilGuide from "./pages/SoilGuide";

const AppRoutes = () => (
    <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/calendar" element={<PlantingCalendar />} />
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
        <Route
            path="/recommendations"
            element={
                <ProtectedRoute>
                    <Recommendations />
                </ProtectedRoute>
            }
        />
        <Route
            path="/tasks"
            element={
                <ProtectedRoute>
                    <Tasks />
                </ProtectedRoute>
            }
        />
        <Route
            path="/harvests"
            element={
                <ProtectedRoute>
                    <HarvestSummary />
                </ProtectedRoute>
            }
        />
        <Route
            path="/gardens/:gardenId/harvests"
            element={
                <ProtectedRoute>
                    <HarvestLog />
                </ProtectedRoute>
            }
        />
        <Route
            path="/soil"
            element={
                <ProtectedRoute>
                    <SoilGuide />
                </ProtectedRoute>
            }
        />
    </Routes>
);

export default AppRoutes;
