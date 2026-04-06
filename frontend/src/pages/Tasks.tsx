import { useState, useEffect, useContext } from "react";
import { Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import api from "../services/api";
import styles from "../styles/Tasks.module.css";

type Task = {
    id: string;
    type: string;
    priority: "high" | "medium" | "low";
    title: string;
    description: string;
    garden_name: string | null;
    garden_id: number | null;
    plant_name: string | null;
    due: "today" | "this_week" | "upcoming";
};

type TaskSummary = {
    total: number;
    high: number;
    medium: number;
    low: number;
};

type Filter = "all" | "today" | "this_week" | "upcoming";

const TYPE_LABELS: Record<string, string> = {
    watering: "Watering",
    growth_stage: "Growth",
    harvest: "Harvest",
    seasonal: "Seasonal",
    frost_warning: "Frost",
};

const DUE_LABELS: Record<string, string> = {
    today: "Today",
    this_week: "This Week",
    upcoming: "Upcoming",
};

const Tasks = () => {
    const auth = useContext(AuthContext);
    const token = auth?.isAuthenticated
        ? localStorage.getItem("token") ?? undefined
        : undefined;

    const [tasks, setTasks] = useState<Task[]>([]);
    const [summary, setSummary] = useState<TaskSummary>({
        total: 0,
        high: 0,
        medium: 0,
        low: 0,
    });
    const [filter, setFilter] = useState<Filter>("all");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchTasks = async () => {
            if (!token) {
                setLoading(false);
                return;
            }
            try {
                const data = await api.getTasks(token);
                setTasks(data.tasks || []);
                setSummary(data.summary || { total: 0, high: 0, medium: 0, low: 0 });
            } catch (err) {
                console.error("Error fetching tasks:", err);
                setError("Failed to load tasks.");
            } finally {
                setLoading(false);
            }
        };
        fetchTasks();
    }, [token]);

    const filteredTasks =
        filter === "all" ? tasks : tasks.filter((t) => t.due === filter);

    if (loading) {
        return (
            <>
                <div className={styles.pageHeader}>
                    <h1 className={styles.pageTitle}>Garden Tasks</h1>
                    <p className={styles.subtitle}>Smart reminders to keep your garden thriving</p>
                </div>
                <div className={styles.container}>
                    <div style={{ display: "flex", justifyContent: "center", gap: "var(--space-md)", marginBottom: "var(--space-xl)" }}>
                        {[1, 2, 3].map((i) => (
                            <div key={i} className="skeleton" style={{ height: "2.5rem", width: "100px", borderRadius: "9999px" }} />
                        ))}
                    </div>
                    {[1, 2, 3].map((i) => (
                        <div key={i} className="skeleton" style={{ height: "80px", borderRadius: "var(--radius-lg)", marginBottom: "var(--space-md)" }} />
                    ))}
                </div>
            </>
        );
    }

    return (
        <>
        <div className={styles.pageHeader}>
            <h1 className={styles.pageTitle}>Garden Tasks</h1>
            <p className={styles.subtitle}>Smart reminders to keep your garden thriving</p>
        </div>
        <div className={styles.container}>

            {error && <p className={styles.errorMessage}>{error}</p>}

            {/* Summary Bar */}
            <div className={styles.summaryBar}>
                <div className={styles.summaryItem}>
                    <span className={`${styles.summaryDot} ${styles.dotHigh}`} />
                    {summary.high} High
                </div>
                <div className={styles.summaryItem}>
                    <span className={`${styles.summaryDot} ${styles.dotMedium}`} />
                    {summary.medium} Medium
                </div>
                <div className={styles.summaryItem}>
                    <span className={`${styles.summaryDot} ${styles.dotLow}`} />
                    {summary.low} Low
                </div>
            </div>

            {/* Filter Tabs */}
            <div className={styles.filterTabs}>
                {(["all", "today", "this_week", "upcoming"] as Filter[]).map(
                    (f) => (
                        <button
                            key={f}
                            className={`${styles.filterTab} ${filter === f ? styles.filterTabActive : ""}`}
                            onClick={() => setFilter(f)}
                        >
                            {f === "all"
                                ? "All"
                                : f === "today"
                                  ? "Today"
                                  : f === "this_week"
                                    ? "This Week"
                                    : "Upcoming"}
                        </button>
                    )
                )}
            </div>

            {/* Task List */}
            {filteredTasks.length === 0 ? (
                <div className={styles.emptyState}>
                    <h2>No tasks{filter !== "all" ? ` for ${DUE_LABELS[filter] || filter}` : ""}</h2>
                    <p>
                        {tasks.length === 0 ? (
                            <>
                                Add plants to your <Link to="/gardens">gardens</Link> to
                                get personalized task reminders.
                            </>
                        ) : (
                            "Try a different filter to see more tasks."
                        )}
                    </p>
                </div>
            ) : (
                <div className={styles.taskList}>
                    {filteredTasks.map((task) => (
                        <div key={task.id} className={styles.taskCard}>
                            <div
                                className={`${styles.taskBorder} ${
                                    task.priority === "high"
                                        ? styles.borderHigh
                                        : task.priority === "medium"
                                          ? styles.borderMedium
                                          : styles.borderLow
                                }`}
                            />
                            <div className={styles.taskContent}>
                                <div className={styles.taskHeader}>
                                    <span
                                        className={`${styles.priorityBadge} ${
                                            task.priority === "high"
                                                ? styles.badgeHigh
                                                : task.priority === "medium"
                                                  ? styles.badgeMedium
                                                  : styles.badgeLow
                                        }`}
                                    >
                                        {task.priority}
                                    </span>
                                    <span className={styles.typeBadge}>
                                        {TYPE_LABELS[task.type] || task.type}
                                    </span>
                                    <h3 className={styles.taskTitle}>
                                        {task.title}
                                    </h3>
                                </div>
                                <p className={styles.taskDescription}>
                                    {task.description}
                                </p>
                                <div className={styles.taskMeta}>
                                    {task.garden_name && task.garden_id && (
                                        <span>
                                            <Link to={`/gardens`}>
                                                {task.garden_name}
                                            </Link>
                                        </span>
                                    )}
                                    {task.plant_name && (
                                        <span>{task.plant_name}</span>
                                    )}
                                    <span
                                        className={`${styles.dueBadge} ${
                                            task.due === "today"
                                                ? styles.dueToday
                                                : task.due === "this_week"
                                                  ? styles.dueWeek
                                                  : styles.dueUpcoming
                                        }`}
                                    >
                                        {DUE_LABELS[task.due] || task.due}
                                    </span>
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

export default Tasks;
