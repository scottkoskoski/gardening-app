import { useState, useEffect, useContext } from "react";
import { Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import api from "../services/api";
import styles from "../styles/PlantingCalendar.module.css";

interface Activity {
    plant_name: string;
    plant_id: number;
    activity: string;
    category: string;
}

interface MonthData {
    month: number;
    month_name: string;
    activities: Activity[];
}

interface CalendarData {
    zone: string;
    calendar: MonthData[];
    current_month: number;
}

const ZONES = [
    "3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b",
    "7a", "7b", "8a", "8b", "9a", "9b", "10a", "10b",
    "11a", "11b", "12a", "12b",
];

const CATEGORY_LABELS: Record<string, string> = {
    planning: "Planning",
    start_indoors: "Start Indoors",
    direct_sow: "Direct Sow",
    transplant: "Transplant",
    harvest: "Harvest",
    maintenance: "Maintenance",
};

const CATEGORY_STYLES: Record<string, string> = {
    planning: styles.categoryPlanning,
    start_indoors: styles.categoryStartIndoors,
    direct_sow: styles.categoryDirectSow,
    transplant: styles.categoryTransplant,
    harvest: styles.categoryHarvest,
    maintenance: styles.categoryMaintenance,
};

const PlantingCalendar = () => {
    const auth = useContext(AuthContext);
    const [calendarData, setCalendarData] = useState<CalendarData | null>(null);
    const [selectedZone, setSelectedZone] = useState<string>("");
    const [userZone, setUserZone] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [mobileMonth, setMobileMonth] = useState(3); // April = index 3 (0-based)

    // Fetch user profile to get their zone
    useEffect(() => {
        const fetchProfile = async () => {
            if (auth?.token) {
                try {
                    const profile = await api.getProfile(auth.token);
                    if (profile?.plant_hardiness_zone) {
                        setUserZone(profile.plant_hardiness_zone);
                        if (!selectedZone) {
                            setSelectedZone(profile.plant_hardiness_zone);
                        }
                    }
                } catch {
                    // User not logged in or profile fetch failed - that's fine
                }
            }
        };
        fetchProfile();
    }, [auth?.token]);

    // Fetch calendar when zone changes
    useEffect(() => {
        if (!selectedZone) return;

        const fetchCalendar = async () => {
            setLoading(true);
            setError(null);
            try {
                const data = await api.getPlantingCalendar(selectedZone);
                setCalendarData(data);
            } catch {
                setError("Failed to load planting calendar. Please try again.");
            } finally {
                setLoading(false);
            }
        };
        fetchCalendar();
    }, [selectedZone]);

    // Group activities by category for the summary
    const getCurrentMonthActivities = (): Record<string, Activity[]> => {
        if (!calendarData) return {};
        const currentMonthData = calendarData.calendar.find(
            (m) => m.month === calendarData.current_month
        );
        if (!currentMonthData) return {};

        const grouped: Record<string, Activity[]> = {};
        for (const act of currentMonthData.activities) {
            if (!grouped[act.category]) grouped[act.category] = [];
            // Avoid duplicate plant names within same category
            if (!grouped[act.category].some((a) => a.plant_name === act.plant_name)) {
                grouped[act.category].push(act);
            }
        }
        return grouped;
    };

    const currentActivities = getCurrentMonthActivities();
    const currentMonthName =
        calendarData?.calendar.find((m) => m.month === calendarData.current_month)
            ?.month_name || "April";

    return (
        <div className={styles.container}>
            <h1 className={styles.pageTitle}>Seasonal Planting Calendar</h1>
            <p className={styles.subtitle}>
                Plan your garden year-round with month-by-month planting activities
            </p>

            {/* Zone Selector */}
            <div className={styles.zoneSelector}>
                <label htmlFor="zone-select">Hardiness Zone:</label>
                <select
                    id="zone-select"
                    className={styles.zoneSelect}
                    value={selectedZone}
                    onChange={(e) => setSelectedZone(e.target.value)}
                >
                    <option value="">Select a zone</option>
                    {ZONES.map((z) => (
                        <option key={z} value={z}>
                            Zone {z}
                        </option>
                    ))}
                </select>
                {userZone && (
                    <span className={styles.userZoneBadge}>
                        Your zone: {userZone}
                    </span>
                )}
            </div>

            {error && <div className={styles.errorMessage}>{error}</div>}
            {loading && <div className={styles.loading}>Loading planting calendar...</div>}

            {calendarData && !loading && (
                <>
                    {/* Current Month Summary */}
                    <div className={styles.currentMonthSummary}>
                        <h2>What to do in {currentMonthName}</h2>
                        {Object.keys(currentActivities).length === 0 ? (
                            <p className={styles.noActivities}>
                                No activities scheduled for this month.
                            </p>
                        ) : (
                            <div className={styles.summaryGrid}>
                                {Object.entries(currentActivities).map(
                                    ([category, activities]) => (
                                        <div
                                            key={category}
                                            className={styles.summaryCategory}
                                        >
                                            <div className={styles.summaryCategoryTitle}>
                                                {CATEGORY_LABELS[category] || category}
                                            </div>
                                            <ul className={styles.summaryPlantList}>
                                                {activities.slice(0, 6).map((act) => (
                                                    <li key={`${act.plant_id}-${act.activity}`}>
                                                        {act.plant_name}
                                                    </li>
                                                ))}
                                                {activities.length > 6 && (
                                                    <li>
                                                        +{activities.length - 6} more
                                                    </li>
                                                )}
                                            </ul>
                                        </div>
                                    )
                                )}
                            </div>
                        )}
                    </div>

                    {/* Legend */}
                    <div className={styles.legend}>
                        {Object.entries(CATEGORY_LABELS).map(([key, label]) => (
                            <div key={key} className={styles.legendItem}>
                                <span
                                    className={`${styles.legendColor} ${CATEGORY_STYLES[key]}`}
                                />
                                <span>{label}</span>
                            </div>
                        ))}
                    </div>

                    {/* Mobile Navigation */}
                    <div className={styles.mobileNav}>
                        <button
                            className={styles.mobileNavButton}
                            onClick={() =>
                                setMobileMonth((prev) => Math.max(0, prev - 1))
                            }
                            disabled={mobileMonth === 0}
                            aria-label="Previous month"
                        >
                            &#8249;
                        </button>
                        <span className={styles.mobileMonthName}>
                            {calendarData.calendar[mobileMonth]?.month_name}
                        </span>
                        <button
                            className={styles.mobileNavButton}
                            onClick={() =>
                                setMobileMonth((prev) => Math.min(11, prev + 1))
                            }
                            disabled={mobileMonth === 11}
                            aria-label="Next month"
                        >
                            &#8250;
                        </button>
                    </div>

                    {/* Mobile Calendar (single month) */}
                    <div className={styles.mobileCalendar}>
                        {calendarData.calendar
                            .filter((_, i) => i === mobileMonth)
                            .map((monthData) => (
                                <div
                                    key={monthData.month}
                                    className={`${styles.mobileMonthCard} ${
                                        monthData.month === calendarData.current_month
                                            ? styles.mobileCurrentMonth
                                            : ""
                                    }`}
                                >
                                    <div className={styles.mobileMonthHeader}>
                                        {monthData.month_name}
                                    </div>
                                    <div className={styles.mobileMonthBody}>
                                        {monthData.activities.length === 0 ? (
                                            <div className={styles.emptyMonth}>
                                                No activities this month
                                            </div>
                                        ) : (
                                            monthData.activities.map((act, idx) => (
                                                <Link
                                                    key={`${act.plant_id}-${act.category}-${idx}`}
                                                    to={`/plants/${act.plant_id}`}
                                                    className={`${styles.mobileActivityBar} ${
                                                        CATEGORY_STYLES[act.category] || ""
                                                    }`}
                                                >
                                                    <span className={styles.mobileActivityPlant}>
                                                        {act.plant_name}
                                                    </span>
                                                    <span className={styles.mobileActivityLabel}>
                                                        {act.activity}
                                                    </span>
                                                </Link>
                                            ))
                                        )}
                                    </div>
                                </div>
                            ))}
                    </div>

                    {/* Desktop Calendar Grid */}
                    <div className={styles.calendarGrid}>
                        {calendarData.calendar.map((monthData) => (
                            <div
                                key={monthData.month}
                                className={`${styles.monthColumn} ${
                                    monthData.month === calendarData.current_month
                                        ? styles.currentMonth
                                        : ""
                                }`}
                            >
                                <div className={styles.monthHeader}>
                                    {monthData.month_name.substring(0, 3)}
                                </div>
                                <div className={styles.monthBody}>
                                    {monthData.activities.length === 0 ? (
                                        <div className={styles.emptyMonth}>
                                            No activities
                                        </div>
                                    ) : (
                                        monthData.activities.map((act, idx) => (
                                            <Link
                                                key={`${act.plant_id}-${act.category}-${idx}`}
                                                to={`/plants/${act.plant_id}`}
                                                className={`${styles.activityBar} ${
                                                    CATEGORY_STYLES[act.category] || ""
                                                }`}
                                                title={`${act.plant_name}: ${act.activity}`}
                                            >
                                                <span className={styles.activityPlant}>
                                                    {act.plant_name}
                                                </span>
                                                <br />
                                                <span className={styles.activityLabel}>
                                                    {act.activity}
                                                </span>
                                            </Link>
                                        ))
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </>
            )}

            {!selectedZone && !loading && (
                <div className={styles.loading}>
                    Select a hardiness zone above to view your planting calendar.
                </div>
            )}
        </div>
    );
};

export default PlantingCalendar;
