import { useState, useEffect, useContext } from "react";
import { Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import api from "../services/api";
import WeatherAlerts from "../components/WeatherAlerts";
import styles from "../styles/Dashboard.module.css";

type Garden = {
    id: number;
    garden_name: string;
    garden_type: string;
    garden_plants: { id: number; plant_name: string; growth_stage: string }[];
};

type WeatherData = {
    current: {
        temperature_2m: number;
        precipitation: number;
        weathercode: number;
    };
    current_units: {
        temperature_2m: string;
    };
};

type ProfileData = {
    zip_code: string;
    plant_hardiness_zone: string;
    city: string;
    state: string;
};

type FrostData = {
    zone: string;
    last_frost: string | null;
    first_frost: string | null;
    growing_season_days: number;
    year_round: boolean;
};

const weatherDescriptions: Record<number, string> = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
};

const Dashboard = () => {
    const auth = useContext(AuthContext);
    const token = auth?.isAuthenticated
        ? localStorage.getItem("token") ?? undefined
        : undefined;

    const [profile, setProfile] = useState<ProfileData | null>(null);
    const [gardens, setGardens] = useState<Garden[]>([]);
    const [weather, setWeather] = useState<WeatherData | null>(null);
    const [frostData, setFrostData] = useState<FrostData | null>(null);
    const [username, setUsername] = useState("");
    const [highPriorityTasks, setHighPriorityTasks] = useState(0);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchDashboardData = async () => {
            if (!token) {
                setLoading(false);
                return;
            }

            try {
                // Fetch user info
                const userResponse = await api.getUser(token);
                setUsername(userResponse.username || "");

                // Fetch profile
                const profileResponse = await api.getProfile(token);
                setProfile(profileResponse);

                // Fetch gardens
                const gardensResponse = await api.getUserGardens(token);
                setGardens(Array.isArray(gardensResponse) ? gardensResponse : []);

                // Fetch tasks summary
                try {
                    const tasksResponse = await api.getTasks(token);
                    if (tasksResponse.summary) {
                        setHighPriorityTasks(tasksResponse.summary.high || 0);
                    }
                } catch {
                    console.warn("Could not fetch tasks data");
                }

                // Fetch weather and frost dates if zip code exists
                if (profileResponse.zip_code) {
                    try {
                        const weatherResponse = await api.getWeather(profileResponse.zip_code);
                        if (weatherResponse.current) {
                            setWeather(weatherResponse);
                        }
                    } catch {
                        // Weather is non-critical, don't block dashboard
                        console.warn("Could not fetch weather data");
                    }

                    try {
                        const frostResponse = await api.getFrostDates(profileResponse.zip_code);
                        setFrostData(frostResponse);
                    } catch {
                        console.warn("Could not fetch frost date data");
                    }
                }
            } catch (err: any) {
                console.error("Error loading dashboard:", err);
                setError("Failed to load dashboard data.");
            } finally {
                setLoading(false);
            }
        };

        fetchDashboardData();
    }, [token]);

    const totalPlants = gardens.reduce(
        (sum, g) => sum + (g.garden_plants?.length || 0),
        0
    );

    if (loading) {
        return (
            <>
                <div className={styles.dashboardHeader}>
                    <h1 className={styles.pageTitle}>Welcome back!</h1>
                    <p className={styles.pageSubtitle}>Loading your garden data...</p>
                </div>
                <div className={styles.container}>
                    <div className={styles.grid}>
                        {[1, 2, 3, 4].map((i) => (
                            <div key={i} className={styles.card}>
                                <div className="skeleton" style={{ height: "1.2rem", width: "50%", marginBottom: "var(--space-md)" }} />
                                <div className="skeleton" style={{ height: "3rem", width: "60%", margin: "0 auto var(--space-sm)" }} />
                                <div className="skeleton" style={{ height: "0.9rem", width: "80%", margin: "0 auto" }} />
                            </div>
                        ))}
                    </div>
                </div>
            </>
        );
    }

    return (
        <>
        <div className={styles.dashboardHeader}>
            <h1 className={styles.pageTitle}>
                Welcome back{username ? `, ${username}` : ""}!
            </h1>
            <p className={styles.pageSubtitle}>Here's what's happening in your garden</p>
        </div>
        <div className={styles.container}>

            {error && <p className={styles.errorMessage}>{error}</p>}

            {token && <WeatherAlerts token={token} />}

            <div className={styles.grid}>
                {/* Weather Card */}
                <div className={styles.card}>
                    <h2 className={styles.cardTitle}>Current Weather</h2>
                    {weather?.current ? (
                        <div className={styles.weatherContent}>
                            <div className={styles.temperature}>
                                {Math.round(weather.current.temperature_2m)}
                                {weather.current_units?.temperature_2m || "°C"}
                            </div>
                            <p className={styles.weatherDescription}>
                                {weatherDescriptions[weather.current.weathercode] || "Unknown"}
                            </p>
                            <p>Precipitation: {weather.current.precipitation} mm</p>
                            {profile?.city && profile?.state && (
                                <p className={styles.location}>
                                    {profile.city}, {profile.state}
                                </p>
                            )}
                        </div>
                    ) : (
                        <p className={styles.emptyState}>
                            {profile?.zip_code
                                ? "Weather data unavailable."
                                : "Set your ZIP code in your "}
                            {!profile?.zip_code && (
                                <Link to="/profile">profile</Link>
                            )}
                            {!profile?.zip_code && " to see weather."}
                        </p>
                    )}
                </div>

                {/* Growing Zone Card */}
                <div className={styles.card}>
                    <h2 className={styles.cardTitle}>Your Growing Zone</h2>
                    {profile?.plant_hardiness_zone ? (
                        <div className={styles.zoneContent}>
                            <div className={styles.zoneBadge}>
                                Zone {profile.plant_hardiness_zone}
                            </div>
                            <p>USDA Plant Hardiness Zone</p>
                            {profile.zip_code && (
                                <p className={styles.location}>
                                    ZIP: {profile.zip_code}
                                </p>
                            )}
                        </div>
                    ) : (
                        <p className={styles.emptyState}>
                            Update your <Link to="/profile">profile</Link> with
                            a ZIP code to see your hardiness zone.
                        </p>
                    )}
                </div>

                {/* Frost Dates Card */}
                <div className={styles.card}>
                    <h2 className={styles.cardTitle}>Frost Dates</h2>
                    {frostData ? (
                        <div className={styles.zoneContent}>
                            {frostData.year_round ? (
                                <p>
                                    Your area (Zone {frostData.zone}) enjoys
                                    year-round growing conditions with no
                                    typical frost dates.
                                </p>
                            ) : (
                                <>
                                    <p>
                                        <strong>Last Frost (Spring):</strong>{" "}
                                        {frostData.last_frost
                                            ? new Date(frostData.last_frost + "T00:00:00").toLocaleDateString(undefined, { month: "long", day: "numeric", year: "numeric" })
                                            : "N/A"}
                                    </p>
                                    <p>
                                        <strong>First Frost (Fall):</strong>{" "}
                                        {frostData.first_frost
                                            ? new Date(frostData.first_frost + "T00:00:00").toLocaleDateString(undefined, { month: "long", day: "numeric", year: "numeric" })
                                            : "N/A"}
                                    </p>
                                    <p>
                                        <strong>Growing Season:</strong>{" "}
                                        {frostData.growing_season_days} days
                                    </p>
                                </>
                            )}
                        </div>
                    ) : (
                        <p className={styles.emptyState}>
                            {profile?.zip_code
                                ? "Frost date data unavailable."
                                : "Set your ZIP code in your "}
                            {!profile?.zip_code && (
                                <Link to="/profile">profile</Link>
                            )}
                            {!profile?.zip_code && " to see frost dates."}
                        </p>
                    )}
                </div>

                {/* Garden Summary Card */}
                <div className={styles.card}>
                    <h2 className={styles.cardTitle}>Garden Summary</h2>
                    {gardens.length > 0 ? (
                        <div className={styles.summaryContent}>
                            <div className={styles.statRow}>
                                <div className={styles.stat}>
                                    <span className={styles.statNumber}>
                                        {gardens.length}
                                    </span>
                                    <span className={styles.statLabel}>
                                        {gardens.length === 1
                                            ? "Garden"
                                            : "Gardens"}
                                    </span>
                                </div>
                                <div className={styles.stat}>
                                    <span className={styles.statNumber}>
                                        {totalPlants}
                                    </span>
                                    <span className={styles.statLabel}>
                                        {totalPlants === 1
                                            ? "Plant"
                                            : "Plants"}
                                    </span>
                                </div>
                            </div>
                            <Link to="/gardens" className={styles.cardLink}>
                                View Gardens
                            </Link>
                            {highPriorityTasks > 0 && (
                                <div className={styles.taskAlert}>
                                    <Link to="/tasks" className={styles.taskAlertLink}>
                                        <span className={styles.taskAlertBadge}>
                                            {highPriorityTasks}
                                        </span>
                                        {" "}high-priority {highPriorityTasks === 1 ? "task" : "tasks"} needing attention
                                    </Link>
                                </div>
                            )}
                        </div>
                    ) : (
                        <p className={styles.emptyState}>
                            No gardens yet.{" "}
                            <Link to="/gardens">Create your first garden</Link>{" "}
                            to get started!
                        </p>
                    )}
                </div>

                {/* Gardens List */}
                <div className={`${styles.card} ${styles.wideCard}`}>
                    <h2 className={styles.cardTitle}>Your Gardens</h2>
                    {gardens.length > 0 ? (
                        <div className={styles.gardenList}>
                            {gardens.map((garden) => (
                                <div
                                    key={garden.id}
                                    className={styles.gardenItem}
                                >
                                    <div className={styles.gardenInfo}>
                                        <h3>{garden.garden_name}</h3>
                                        <span className={styles.gardenType}>
                                            {garden.garden_type}
                                        </span>
                                    </div>
                                    <div className={styles.gardenPlantCount}>
                                        {garden.garden_plants?.length || 0}{" "}
                                        {(garden.garden_plants?.length || 0) ===
                                        1
                                            ? "plant"
                                            : "plants"}
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className={styles.emptyState}>
                            <Link to="/gardens">Create a garden</Link> to start
                            tracking your plants.
                        </p>
                    )}
                </div>
            </div>
        </div>
        </>
    );
};

export default Dashboard;
