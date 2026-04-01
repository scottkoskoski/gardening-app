import { useState, useEffect, useContext } from "react";
import { useParams, Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import api from "../services/api";
import styles from "../styles/HarvestLog.module.css";

type HarvestEntry = {
    id: number;
    garden_id: number;
    plant_id: number;
    plant_name: string;
    harvest_date: string;
    quantity: number;
    unit: string;
    quality: string | null;
    notes: string | null;
    created_at: string;
};

type GardenPlant = {
    id: number;
    plant_id: number;
    plant_name: string;
    growth_stage: string;
};

const UNITS = ["lbs", "kg", "oz", "count", "bunches", "bushels"];
const QUALITIES = ["excellent", "good", "fair", "poor"];

const HarvestLog = () => {
    const { gardenId } = useParams<{ gardenId: string }>();
    const auth = useContext(AuthContext);
    const token = auth?.isAuthenticated
        ? localStorage.getItem("token") ?? undefined
        : undefined;

    const [harvests, setHarvests] = useState<HarvestEntry[]>([]);
    const [gardenName, setGardenName] = useState("");
    const [gardenPlants, setGardenPlants] = useState<GardenPlant[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showForm, setShowForm] = useState(false);

    const [formData, setFormData] = useState({
        plant_id: 0,
        quantity: "",
        unit: "lbs",
        quality: "",
        harvest_date: new Date().toISOString().split("T")[0],
        notes: "",
    });

    const gardenIdNum = gardenId ? parseInt(gardenId, 10) : 0;

    useEffect(() => {
        const fetchData = async () => {
            if (!token || !gardenIdNum) {
                setLoading(false);
                return;
            }

            try {
                const harvestRes = await api.getHarvests(gardenIdNum, token);
                setHarvests(harvestRes.harvests || []);
                setGardenName(harvestRes.garden_name || "");

                const gardenRes = await api.get(
                    `/user_gardens/${gardenIdNum}`,
                    token
                );
                setGardenPlants(gardenRes.garden_plants || []);

                if (
                    gardenRes.garden_plants &&
                    gardenRes.garden_plants.length > 0
                ) {
                    setFormData((prev) => ({
                        ...prev,
                        plant_id: gardenRes.garden_plants[0].plant_id,
                    }));
                }
            } catch (err: any) {
                console.error("Error fetching harvest data:", err);
                setError(err.message || "Failed to load harvest data");
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [token, gardenIdNum]);

    const handleInputChange = (
        e: React.ChangeEvent<
            HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
        >
    ) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleLogHarvest = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!token) return;

        try {
            const payload = {
                garden_id: gardenIdNum,
                plant_id: Number(formData.plant_id),
                quantity: parseFloat(formData.quantity),
                unit: formData.unit,
                quality: formData.quality || null,
                harvest_date: formData.harvest_date
                    ? new Date(formData.harvest_date).toISOString()
                    : null,
                notes: formData.notes || null,
            };

            await api.logHarvest(payload, token);

            const harvestRes = await api.getHarvests(gardenIdNum, token);
            setHarvests(harvestRes.harvests || []);

            setShowForm(false);
            setFormData({
                plant_id:
                    gardenPlants.length > 0 ? gardenPlants[0].plant_id : 0,
                quantity: "",
                unit: "lbs",
                quality: "",
                harvest_date: new Date().toISOString().split("T")[0],
                notes: "",
            });
        } catch (err: any) {
            console.error("Error logging harvest:", err);
            setError(err.message || "Failed to log harvest");
        }
    };

    const handleDelete = async (harvestId: number) => {
        if (!token) return;
        if (
            !window.confirm(
                "Are you sure you want to delete this harvest entry?"
            )
        )
            return;

        try {
            await api.deleteHarvest(harvestId, token);
            setHarvests((prev) => prev.filter((h) => h.id !== harvestId));
        } catch (err: any) {
            console.error("Error deleting harvest:", err);
            setError(err.message || "Failed to delete harvest");
        }
    };

    const getQualityClass = (quality: string | null) => {
        if (!quality) return "";
        const classMap: Record<string, string> = {
            excellent: styles.badgeExcellent,
            good: styles.badgeGood,
            fair: styles.badgeFair,
            poor: styles.badgePoor,
        };
        return classMap[quality] || "";
    };

    // Compute summary stats
    const totalHarvests = harvests.length;
    const unitCounts: Record<string, number> = {};
    harvests.forEach((h) => {
        unitCounts[h.unit] = (unitCounts[h.unit] || 0) + h.quantity;
    });
    let mostCommonUnit = "";
    let maxCount = 0;
    Object.entries(unitCounts).forEach(([unit, qty]) => {
        if (qty > maxCount) {
            maxCount = qty;
            mostCommonUnit = unit;
        }
    });

    if (loading) {
        return (
            <div className={styles.container}>
                <p>Loading harvest data...</p>
            </div>
        );
    }

    return (
        <div className={styles.container}>
            <Link to="/gardens" className={styles.backLink}>
                Back to Gardens
            </Link>

            <h1 className={styles.pageTitle}>
                {gardenName ? `${gardenName} - Harvests` : "Harvest Log"}
            </h1>
            {gardenName && (
                <p className={styles.gardenSubtitle}>
                    Track and manage your harvests
                </p>
            )}

            {error && (
                <div className={styles.errorMessage}>
                    <p>{error}</p>
                    <button
                        onClick={() => setError(null)}
                        className={styles.closeButton}
                    >
                        x
                    </button>
                </div>
            )}

            {/* Summary Stats */}
            {totalHarvests > 0 && (
                <div className={styles.statsRow}>
                    <div className={styles.statCard}>
                        <p className={styles.statValue}>{totalHarvests}</p>
                        <p className={styles.statLabel}>Total Harvests</p>
                    </div>
                    {mostCommonUnit && (
                        <div className={styles.statCard}>
                            <p className={styles.statValue}>
                                {maxCount.toFixed(1)}
                            </p>
                            <p className={styles.statLabel}>
                                Total ({mostCommonUnit})
                            </p>
                        </div>
                    )}
                </div>
            )}

            {/* Log Harvest Button */}
            <button
                onClick={() => setShowForm(!showForm)}
                className={styles.primaryButton}
            >
                {showForm ? "Cancel" : "Log Harvest"}
            </button>

            {/* Log Harvest Form */}
            {showForm && (
                <div className={styles.formContainer}>
                    <h2>Log Harvest</h2>
                    <form onSubmit={handleLogHarvest} className={styles.form}>
                        <div className={styles.formGroup}>
                            <label htmlFor="plant_id">Plant</label>
                            <select
                                id="plant_id"
                                name="plant_id"
                                value={formData.plant_id}
                                onChange={handleInputChange}
                                required
                            >
                                <option value="">Select Plant</option>
                                {gardenPlants.map((gp) => (
                                    <option
                                        key={gp.plant_id}
                                        value={gp.plant_id}
                                    >
                                        {gp.plant_name}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div className={styles.formGroup}>
                            <label htmlFor="quantity">Quantity</label>
                            <input
                                type="number"
                                id="quantity"
                                name="quantity"
                                value={formData.quantity}
                                onChange={handleInputChange}
                                min="0"
                                step="0.1"
                                required
                            />
                        </div>

                        <div className={styles.formGroup}>
                            <label htmlFor="unit">Unit</label>
                            <select
                                id="unit"
                                name="unit"
                                value={formData.unit}
                                onChange={handleInputChange}
                                required
                            >
                                {UNITS.map((u) => (
                                    <option key={u} value={u}>
                                        {u}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div className={styles.formGroup}>
                            <label htmlFor="quality">Quality</label>
                            <select
                                id="quality"
                                name="quality"
                                value={formData.quality}
                                onChange={handleInputChange}
                            >
                                <option value="">-- Optional --</option>
                                {QUALITIES.map((q) => (
                                    <option key={q} value={q}>
                                        {q.charAt(0).toUpperCase() + q.slice(1)}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div className={styles.formGroup}>
                            <label htmlFor="harvest_date">Date</label>
                            <input
                                type="date"
                                id="harvest_date"
                                name="harvest_date"
                                value={formData.harvest_date}
                                onChange={handleInputChange}
                            />
                        </div>

                        <div className={styles.formGroupFull}>
                            <label htmlFor="notes">Notes</label>
                            <textarea
                                id="notes"
                                name="notes"
                                value={formData.notes}
                                onChange={handleInputChange}
                                placeholder="Optional notes about this harvest..."
                            />
                        </div>

                        <button type="submit" className={styles.submitButton}>
                            Log Harvest
                        </button>
                    </form>
                </div>
            )}

            {/* Harvest History Table */}
            {harvests.length === 0 ? (
                <p className={styles.noHarvests}>
                    No harvests logged yet. Click "Log Harvest" to record your
                    first harvest!
                </p>
            ) : (
                <table className={styles.harvestTable}>
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Plant</th>
                            <th>Quantity</th>
                            <th>Quality</th>
                            <th>Notes</th>
                            <th></th>
                        </tr>
                    </thead>
                    <tbody>
                        {harvests.map((h) => (
                            <tr key={h.id}>
                                <td>
                                    {h.harvest_date
                                        ? new Date(
                                              h.harvest_date
                                          ).toLocaleDateString()
                                        : "N/A"}
                                </td>
                                <td>{h.plant_name}</td>
                                <td>
                                    {h.quantity} {h.unit}
                                </td>
                                <td>
                                    {h.quality ? (
                                        <span
                                            className={`${styles.badge} ${getQualityClass(h.quality)}`}
                                        >
                                            {h.quality}
                                        </span>
                                    ) : (
                                        "-"
                                    )}
                                </td>
                                <td className={styles.notesCell}>
                                    {h.notes || "-"}
                                </td>
                                <td>
                                    <button
                                        onClick={() => handleDelete(h.id)}
                                        className={styles.deleteButton}
                                        title="Delete harvest"
                                    >
                                        Delete
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
};

export default HarvestLog;
