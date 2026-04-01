import { useState, useEffect, useContext } from "react";
import { useParams, Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import api from "../services/api";
import styles from "../styles/GardenJournal.module.css";

type JournalEntry = {
    id: number;
    garden_id: number;
    user_id: number;
    entry_type: string;
    title: string;
    notes: string | null;
    entry_date: string;
    created_at: string;
};

const ENTRY_TYPES = [
    "watering",
    "fertilizing",
    "pruning",
    "planting",
    "harvesting",
    "pest_control",
    "observation",
    "other",
];

const BADGE_CLASS_MAP: Record<string, string> = {
    watering: styles.badgeWatering,
    fertilizing: styles.badgeFertilizing,
    pruning: styles.badgePruning,
    planting: styles.badgePlanting,
    harvesting: styles.badgeHarvesting,
    pest_control: styles.badgePestControl,
    observation: styles.badgeObservation,
    other: styles.badgeOther,
};

const formatEntryType = (type: string) =>
    type.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

const GardenJournal = () => {
    const { gardenId } = useParams<{ gardenId: string }>();
    const auth = useContext(AuthContext);
    const token = auth?.isAuthenticated
        ? localStorage.getItem("token") ?? undefined
        : undefined;

    const [entries, setEntries] = useState<JournalEntry[]>([]);
    const [gardenName, setGardenName] = useState("");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showForm, setShowForm] = useState(false);
    const [expandedNotes, setExpandedNotes] = useState<Set<number>>(new Set());

    const [formData, setFormData] = useState({
        entry_type: "observation",
        title: "",
        notes: "",
        entry_date: new Date().toISOString().slice(0, 10),
    });

    useEffect(() => {
        const fetchEntries = async () => {
            if (!token || !gardenId) {
                setLoading(false);
                return;
            }
            try {
                const response = await api.getJournalEntries(
                    Number(gardenId),
                    token
                );
                setEntries(response.entries || []);
                setGardenName(response.garden_name || "");
            } catch (err: any) {
                setError(err.message || "Failed to load journal entries");
            } finally {
                setLoading(false);
            }
        };
        fetchEntries();
    }, [token, gardenId]);

    const handleInputChange = (
        e: React.ChangeEvent<
            HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
        >
    ) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!token || !gardenId) return;

        try {
            const payload = {
                garden_id: Number(gardenId),
                entry_type: formData.entry_type,
                title: formData.title,
                notes: formData.notes || null,
                entry_date: formData.entry_date
                    ? new Date(formData.entry_date).toISOString()
                    : undefined,
            };

            const response = await api.createJournalEntry(payload, token);

            if (response.entry) {
                setEntries((prev) => [response.entry, ...prev]);
            }
            setShowForm(false);
            setFormData({
                entry_type: "observation",
                title: "",
                notes: "",
                entry_date: new Date().toISOString().slice(0, 10),
            });
        } catch (err: any) {
            setError(err.message || "Failed to create journal entry");
        }
    };

    const handleDelete = async (entryId: number) => {
        if (!token) return;
        if (!window.confirm("Are you sure you want to delete this entry?"))
            return;

        try {
            await api.deleteJournalEntry(entryId, token);
            setEntries((prev) => prev.filter((e) => e.id !== entryId));
        } catch (err: any) {
            setError(err.message || "Failed to delete journal entry");
        }
    };

    const toggleNotes = (entryId: number) => {
        setExpandedNotes((prev) => {
            const next = new Set(prev);
            if (next.has(entryId)) {
                next.delete(entryId);
            } else {
                next.add(entryId);
            }
            return next;
        });
    };

    if (loading) {
        return (
            <div className={styles.container}>
                <p>Loading journal...</p>
            </div>
        );
    }

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <h1>{gardenName ? `${gardenName} Journal` : "Garden Journal"}</h1>
                <div className={styles.headerActions}>
                    <Link to="/gardens" className={styles.backLink}>
                        Back to Gardens
                    </Link>
                    <button
                        onClick={() => setShowForm(!showForm)}
                        className={styles.newEntryButton}
                    >
                        {showForm ? "Cancel" : "New Entry"}
                    </button>
                </div>
            </div>

            {error && (
                <div className={styles.errorMessage}>
                    <p>{error}</p>
                    <button
                        onClick={() => setError(null)}
                        className={styles.closeButton}
                    >
                        ×
                    </button>
                </div>
            )}

            {showForm && (
                <div className={styles.formContainer}>
                    <h2>New Journal Entry</h2>
                    <form onSubmit={handleSubmit} className={styles.form}>
                        <div className={styles.formGroup}>
                            <label htmlFor="entry_type">Entry Type:</label>
                            <select
                                id="entry_type"
                                name="entry_type"
                                value={formData.entry_type}
                                onChange={handleInputChange}
                                required
                            >
                                {ENTRY_TYPES.map((type) => (
                                    <option key={type} value={type}>
                                        {formatEntryType(type)}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div className={styles.formGroup}>
                            <label htmlFor="title">Title:</label>
                            <input
                                type="text"
                                id="title"
                                name="title"
                                value={formData.title}
                                onChange={handleInputChange}
                                required
                                maxLength={200}
                                placeholder="What did you do?"
                            />
                        </div>

                        <div className={styles.formGroup}>
                            <label htmlFor="notes">Notes:</label>
                            <textarea
                                id="notes"
                                name="notes"
                                value={formData.notes}
                                onChange={handleInputChange}
                                placeholder="Additional details (optional)"
                            />
                        </div>

                        <div className={styles.formGroup}>
                            <label htmlFor="entry_date">Date:</label>
                            <input
                                type="date"
                                id="entry_date"
                                name="entry_date"
                                value={formData.entry_date}
                                onChange={handleInputChange}
                            />
                        </div>

                        <div className={styles.formActions}>
                            <button
                                type="submit"
                                className={styles.submitButton}
                            >
                                Save Entry
                            </button>
                            <button
                                type="button"
                                onClick={() => setShowForm(false)}
                                className={styles.cancelButton}
                            >
                                Cancel
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {entries.length === 0 ? (
                <div className={styles.emptyState}>
                    <p>No journal entries yet.</p>
                    <span>
                        Click "New Entry" to start tracking your garden
                        activities.
                    </span>
                </div>
            ) : (
                <div className={styles.timeline}>
                    {entries.map((entry) => {
                        const isExpanded = expandedNotes.has(entry.id);
                        const hasLongNotes =
                            entry.notes && entry.notes.length > 200;

                        return (
                            <div
                                key={entry.id}
                                className={styles.timelineEntry}
                            >
                                <div className={styles.entryHeader}>
                                    <div className={styles.entryMeta}>
                                        <span
                                            className={`${styles.badge} ${
                                                BADGE_CLASS_MAP[
                                                    entry.entry_type
                                                ] || styles.badgeOther
                                            }`}
                                        >
                                            {formatEntryType(entry.entry_type)}
                                        </span>
                                        <span className={styles.entryDate}>
                                            {new Date(
                                                entry.entry_date
                                            ).toLocaleDateString("en-US", {
                                                year: "numeric",
                                                month: "long",
                                                day: "numeric",
                                            })}
                                        </span>
                                    </div>
                                    <button
                                        onClick={() => handleDelete(entry.id)}
                                        className={styles.deleteEntryButton}
                                        title="Delete entry"
                                    >
                                        ×
                                    </button>
                                </div>
                                <div className={styles.entryTitle}>
                                    {entry.title}
                                </div>
                                {entry.notes && (
                                    <>
                                        <div
                                            className={`${styles.entryNotes} ${
                                                !isExpanded && hasLongNotes
                                                    ? styles.entryNotesCollapsed
                                                    : ""
                                            }`}
                                        >
                                            {entry.notes}
                                        </div>
                                        {hasLongNotes && (
                                            <button
                                                onClick={() =>
                                                    toggleNotes(entry.id)
                                                }
                                                className={styles.expandButton}
                                            >
                                                {isExpanded
                                                    ? "Show less"
                                                    : "Show more"}
                                            </button>
                                        )}
                                    </>
                                )}
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
};

export default GardenJournal;
