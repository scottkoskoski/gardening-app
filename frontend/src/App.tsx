import { useLocation } from "react-router-dom";
import AppRoutes from "./routes";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";

function App() {
    const location = useLocation();

    return (
        <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
            <Navbar />
            <div
                key={location.pathname}
                style={{
                    flex: 1,
                    animation: "routeFadeIn 0.3s ease both",
                }}
            >
                <AppRoutes />
            </div>
            <Footer />
        </div>
    );
}

export default App;
