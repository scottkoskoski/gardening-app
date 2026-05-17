import { useState, useEffect, useContext } from "react";
import { Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import api from "../services/api";
import styles from "../styles/Irrigation.module.css";

type Urgency = "today" | "soon" | "later" | "skip";

type IrrigationItem = {
    garden_plant_id: number;
    plant_id: number;
    plant_name: string;
    garden_id: number;
    garden_name: string;
    growth_stage: string | null;
    water_needs: "Low" | "Medium" | "High" | string;
    frequency_days: number;
    next_watering: string;
    days_until: number;
    skip_today: boolean;
    urgency: Urgency;
    amount_guidance: string;
    reasoning: string[];
};

type IrrigationSummary = {
    total: number;
    today: number;
    soon: number;
    later: number;
    skip: number;
};

type IrrigationResponse = {
    schedule: IrrigationItem[];
    summary: IrrigationSummary;
    weather: { temperature: number | null; precipitation: number | null } | null;
    zip_code: string | null;
};

type Filter = "all" | Urgency;

const URGENCY_LABELS: Record<Urgency, string> = {
    today: "Water today",
    soon: "Water soon",
    later: "Later this week",
    skip: "Skip today",
};

const FILTER_LABELS: Record<Filter, string> = {
    all: "All",
    today: "Today",
    soon: "Soon",
    later: "Later",
    skip: "Skip",
};

const formatDate = (iso: string) => {
    const d = new Date(iso + "T00:00:00");
    return d.toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric" });
};

const formatDaysUntil = (days: number, skip: boolean) => {
    if (skip) return "Skip today";
    if (days <= 0) return "Today";
    if (days === 1) return "Tomorrow";
    return `In ${days} days`;
};

const Irrigation = () => {
    const auth = useContext(AuthContext);
    const token = auth?.isAuthenticated
        ? localStorage.getItem("token") ?? undefined
        : undefined;

    const [data, setData] = useState<IrrigationResponse | null>(null);
    const [filter, setFilter] = useState<Filter>("all");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchSchedule = async () => {
            if (!token) {
                setLoading(false);
                return;
            }
            try {
                const response = await api.getIrrigationSchedule(token);
                setData(response);
            } catch (err) {
                console.error("Error fetching irrigation schedule:", err);
                setError("Failed to load irrigation schedule.");
            } finally {
                setLoading(false);
            }
        };
        fetchSchedule();
    }, [token]);

    const schedule = data?.schedule ?? [];
    const summary = data?.summary ?? { total: 0, today: 0, soon: 0, later: 0, skip: 0 };
    const filtered = filter === "all" ? schedule : schedule.filter((s) => s.urgency === filter);

    if (loading) {
        return (
            <>
                <div className={styles.pageHeader}>
                    <h1 className={styles.pageTitle}>Irrigation Schedule</h1>
                    <p className={styles.subtitle}>How often to water each of your plants</p>
                </div>
                <div className={styles.container}>
                    {[1, 2, 3].map((i) => (
                        <div
                            key={i}
                            className="skeleton"
                            style={{ height: "120px", borderRadius: "var(--radius-lg)", marginBottom: "var(--space-md)" }}
                        />
                    ))}
                </div>
            </>
        );
    }

    return (
        <>
            <div className={styles.pageHeader}>
                <h1 className={styles.pageTitle}>Irrigation Schedule</h1>
                <p className={styles.subtitle}>How often to water each of your plants</p>
            </div>
            <div className={styles.container}>
                {error && <p className={styles.errorMessage}>{error}</p>}

                {data?.weather && (
                    <div className={styles.weatherBanner}>
                        <span className={styles.weatherLabel}>Current conditions:</span>{" "}
                        {data.weather.temperature !== null && (
                            <span>{Math.round(data.weather.temperature)}°C</span>
                        )}
                        {data.weather.precipitation !== null && (
                            <span> · {data.weather.precipitation} mm precipitation</span>
                        )}
                        {data.zip_code && <span className={styles.weatherZip}> (ZIP {data.zip_code})</span>}
                    </div>
                )}

                <div className={styles.summaryBar}>
                    <div className={styles.summaryItem}>
                        <span className={`${styles.summaryDot} ${styles.dotToday}`} />
                        {summary.today} Today
                    </div>
                    <div className={styles.summaryItem}>
                        <span className={`${styles.summaryDot} ${styles.dotSoon}`} />
                        {summary.soon} Soon
                    </div>
                    <div className={styles.summaryItem}>
                        <span className={`${styles.summaryDot} ${styles.dotLater}`} />
                        {summary.later} Later
                    </div>
                    {summary.skip > 0 && (
                        <div className={styles.summaryItem}>
                            <span className={`${styles.summaryDot} ${styles.dotSkip}`} />
                            {summary.skip} Skip
                        </div>
                    )}
                </div>

                <div className={styles.filterTabs}>
                    {(["all", "today", "soon", "later", "skip"] as Filter[]).map((f) => (
                        <button
                            key={f}
                            className={`${styles.filterTab} ${filter === f ? styles.filterTabActive : ""}`}
                            onClick={() => setFilter(f)}
                        >
                            {FILTER_LABELS[f]}
                        </button>
                    ))}
                </div>

                {filtered.length === 0 ? (
                    <div className={styles.emptyState}>
                        <h2>Nothing to water{filter !== "all" ? ` (${FILTER_LABELS[filter]})` : ""}</h2>
                        <p>
                            {schedule.length === 0 ? (
                                <>
                                    Add plants to your <Link to="/gardens">gardens</Link> to
                                    get personalized watering recommendations.
                                </>
                            ) : (
                                "Try a different filter to see more plants."
                            )}
                        </p>
                    </div>
                ) : (
                    <div className={styles.scheduleList}>
                        {filtered.map((item) => (
                            <div key={item.garden_plant_id} className={styles.scheduleCard}>
                                <div
                                    className={`${styles.urgencyBorder} ${
                                        item.urgency === "today"
                                            ? styles.borderToday
                                            : item.urgency === "soon"
                                              ? styles.borderSoon
                                              : item.urgency === "skip"
                                                ? styles.borderSkip
                                                : styles.borderLater
                                    }`}
                                />
                                <div className={styles.cardContent}>
                                    <div className={styles.cardHeader}>
                                        <h3 className={styles.plantName}>{item.plant_name}</h3>
                                        <span
                                            className={`${styles.urgencyBadge} ${
                                                item.urgency === "today"
                                                    ? styles.badgeToday
                                                    : item.urgency === "soon"
                                                      ? styles.badgeSoon
                                                      : item.urgency === "skip"
                                                        ? styles.badgeSkip
                                                        : styles.badgeLater
                                            }`}
                                        >
                                            {URGENCY_LABELS[item.urgency]}
                                        </span>
                                    </div>

                                    <div className={styles.cardStats}>
                                        <div className={styles.stat}>
                                            <span className={styles.statLabel}>Frequency</span>
                                            <span className={styles.statValue}>
                                                Every {item.frequency_days}{" "}
                                                {item.frequency_days === 1 ? "day" : "days"}
                                            </span>
                                        </div>
                                        <div className={styles.stat}>
                                            <span className={styles.statLabel}>Next watering</span>
                                            <span className={styles.statValue}>
                                                {formatDaysUntil(item.days_until, item.skip_today)}
                                                <span className={styles.statDate}>
                                                    {" "}
                                                    · {formatDate(item.next_watering)}
                                                </span>
                                            </span>
                                        </div>
                                        <div className={styles.stat}>
                                            <span className={styles.statLabel}>Water needs</span>
                                            <span className={styles.statValue}>
                                                {item.water_needs}
                                            </span>
                                        </div>
                                    </div>

                                    <p className={styles.amountGuidance}>{item.amount_guidance}</p>

                                    {item.reasoning.length > 0 && (
                                        <ul className={styles.reasoning}>
                                            {item.reasoning.map((r, idx) => (
                                                <li key={idx}>{r}</li>
                                            ))}
                                        </ul>
                                    )}

                                    <div className={styles.cardMeta}>
                                        <Link to="/gardens">{item.garden_name}</Link>
                                        {item.growth_stage && <span>{item.growth_stage}</span>}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </>
    );
};

export default Irrigation;
