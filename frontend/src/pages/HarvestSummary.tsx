import { useState, useEffect, useContext } from "react";
import { Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import api from "../services/api";
import styles from "../styles/HarvestSummary.module.css";

type PlantSummary = {
    plant_name: string;
    total_quantity: number;
    unit: string;
};

type MonthlyData = {
    year: number;
    month: number;
    count: number;
    total_quantity: number;
};

type GardenInfo = {
    id: number;
    garden_name: string;
};

type SummaryData = {
    total_harvests: number;
    plants_summary: PlantSummary[];
    monthly_data: MonthlyData[];
    best_plants: PlantSummary[];
    gardens: GardenInfo[];
};

const MONTH_NAMES = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

const HarvestSummary = () => {
    const auth = useContext(AuthContext);
    const token = auth?.isAuthenticated
        ? localStorage.getItem("token") ?? undefined
        : undefined;

    const [summary, setSummary] = useState<SummaryData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchSummary = async () => {
            if (!token) {
                setLoading(false);
                return;
            }

            try {
                const data = await api.getHarvestSummary(token);
                setSummary(data);
            } catch (err: any) {
                console.error("Error fetching harvest summary:", err);
                setError(err.message || "Failed to load harvest summary");
            } finally {
                setLoading(false);
            }
        };

        fetchSummary();
    }, [token]);

    if (loading) {
        return (
            <>
                <div className={styles.pageHeader}>
                    <h1 className={styles.pageTitle}>Harvest Summary</h1>
                    <p className={styles.pageSubtitle}>Track your garden's productivity</p>
                </div>
                <div className={styles.container}>
                    <div style={{ display: "flex", gap: "var(--space-lg)", marginBottom: "var(--space-xl)" }}>
                        {[1, 2, 3].map((i) => (
                            <div key={i} className="skeleton" style={{ height: "100px", flex: 1, borderRadius: "var(--radius-xl)" }} />
                        ))}
                    </div>
                </div>
            </>
        );
    }

    if (error) {
        return (
            <>
                <div className={styles.pageHeader}>
                    <h1 className={styles.pageTitle}>Harvest Summary</h1>
                    <p className={styles.pageSubtitle}>Track your garden's productivity</p>
                </div>
                <div className={styles.container}>
                    <p className={styles.noData}>{error}</p>
                </div>
            </>
        );
    }

    if (!summary) {
        return (
            <>
                <div className={styles.pageHeader}>
                    <h1 className={styles.pageTitle}>Harvest Summary</h1>
                    <p className={styles.pageSubtitle}>Track your garden's productivity</p>
                </div>
                <div className={styles.container}>
                    <p className={styles.noData}>No harvest data available.</p>
                </div>
            </>
        );
    }

    // Compute total quantity across all plants (using most common unit)
    const unitTotals: Record<string, number> = {};
    summary.plants_summary.forEach((p) => {
        unitTotals[p.unit] = (unitTotals[p.unit] || 0) + p.total_quantity;
    });
    let primaryUnit = "";
    let primaryTotal = 0;
    Object.entries(unitTotals).forEach(([unit, total]) => {
        if (total > primaryTotal) {
            primaryTotal = total;
            primaryUnit = unit;
        }
    });

    // Compute max for bar chart scaling
    const maxMonthlyCount =
        summary.monthly_data.length > 0
            ? Math.max(...summary.monthly_data.map((m) => m.count))
            : 1;

    return (
        <>
        <div className={styles.pageHeader}>
            <h1 className={styles.pageTitle}>Harvest Summary</h1>
            <p className={styles.pageSubtitle}>Track your garden's productivity</p>
        </div>
        <div className={styles.container}>

            {/* Summary Stats */}
            <div className={styles.statsRow}>
                <div className={styles.statCard}>
                    <p className={styles.statValue}>{summary.total_harvests}</p>
                    <p className={styles.statLabel}>Total Harvests</p>
                </div>
                {primaryUnit && (
                    <div className={styles.statCard}>
                        <p className={styles.statValue}>
                            {primaryTotal.toFixed(1)}
                        </p>
                        <p className={styles.statLabel}>
                            Total Yield ({primaryUnit})
                        </p>
                    </div>
                )}
                <div className={styles.statCard}>
                    <p className={styles.statValue}>
                        {summary.plants_summary.length}
                    </p>
                    <p className={styles.statLabel}>Plant Varieties</p>
                </div>
            </div>

            {/* Top Performers */}
            {summary.best_plants.length > 0 && (
                <div className={styles.section}>
                    <h2 className={styles.sectionTitle}>Top Performers</h2>
                    <ul className={styles.performersList}>
                        {summary.best_plants.map((plant, index) => (
                            <li
                                key={`${plant.plant_name}-${plant.unit}`}
                                className={styles.performerItem}
                            >
                                <span className={styles.performerRank}>
                                    #{index + 1}
                                </span>
                                <span className={styles.performerName}>
                                    {plant.plant_name}
                                </span>
                                <span className={styles.performerQuantity}>
                                    {plant.total_quantity} {plant.unit}
                                </span>
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Harvests by Month Chart */}
            {summary.monthly_data.length > 0 && (
                <div className={styles.section}>
                    <h2 className={styles.sectionTitle}>Harvests by Month</h2>
                    <div className={styles.chartContainer}>
                        {summary.monthly_data.map((m) => {
                            const heightPct =
                                maxMonthlyCount > 0
                                    ? (m.count / maxMonthlyCount) * 100
                                    : 0;
                            return (
                                <div
                                    key={`${m.year}-${m.month}`}
                                    className={styles.chartBar}
                                >
                                    <span className={styles.barValue}>
                                        {m.count}
                                    </span>
                                    <div
                                        className={styles.bar}
                                        style={{
                                            height: `${Math.max(heightPct, 2)}%`,
                                        }}
                                        title={`${MONTH_NAMES[m.month - 1]} ${m.year}: ${m.count} harvests, ${m.total_quantity} total`}
                                    />
                                    <span className={styles.barLabel}>
                                        {MONTH_NAMES[m.month - 1]}{" "}
                                        {String(m.year).slice(2)}
                                    </span>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}

            {/* All Plants Summary Table */}
            {summary.plants_summary.length > 0 && (
                <div className={styles.section}>
                    <h2 className={styles.sectionTitle}>Yield by Plant</h2>
                    <table className={styles.summaryTable}>
                        <thead>
                            <tr>
                                <th>Plant</th>
                                <th>Total Quantity</th>
                                <th>Unit</th>
                            </tr>
                        </thead>
                        <tbody>
                            {summary.plants_summary.map((p) => (
                                <tr key={`${p.plant_name}-${p.unit}`}>
                                    <td>{p.plant_name}</td>
                                    <td>{p.total_quantity}</td>
                                    <td>{p.unit}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {/* Garden Links */}
            {summary.gardens.length > 0 && (
                <div className={styles.section}>
                    <h2 className={styles.sectionTitle}>Garden Harvests</h2>
                    <div className={styles.gardenLinks}>
                        {summary.gardens.map((g) => (
                            <Link
                                key={g.id}
                                to={`/gardens/${g.id}/harvests`}
                                className={styles.gardenLink}
                            >
                                {g.garden_name}
                            </Link>
                        ))}
                    </div>
                </div>
            )}
        </div>
        </>
    );
};

export default HarvestSummary;
