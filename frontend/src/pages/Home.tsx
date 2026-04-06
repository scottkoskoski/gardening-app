import { useEffect, useState, useCallback, useRef } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";
import styles from "../styles/Home.module.css";

type Plant = {
    id: number;
    name: string;
    description: string;
    growingSeason: string;
    waterNeeds: string;
    sunlight: string;
    spaceRequired: string;
    requiresGreenhouse: boolean;
    suitableForContainers: boolean;
    imageUrl: string | null;
};

const SUNLIGHT_OPTIONS = ["Full Sun", "Partial Sun", "Partial Shade", "Full Shade"];
const WATER_OPTIONS = ["Low", "Medium", "High"];
const SEASON_OPTIONS = ["Spring", "Summer", "Fall", "Winter"];
const SPACE_OPTIONS = ["Small", "Medium", "Large"];

type Filters = {
    search: string;
    sunlight: string;
    water_needs: string;
    growing_season: string;
    space_required: string;
    containers: string;
    greenhouse: string;
};

const DEFAULT_FILTERS: Filters = {
    search: "",
    sunlight: "",
    water_needs: "",
    growing_season: "",
    space_required: "",
    containers: "",
    greenhouse: "",
};

const Home = () => {
    const [plants, setPlants] = useState<Plant[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);
    const [filters, setFilters] = useState<Filters>(DEFAULT_FILTERS);
    const [searchInput, setSearchInput] = useState("");
    const [filtersOpen, setFiltersOpen] = useState(false);
    const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

    const activeFilterCount = Object.entries(filters).filter(
        ([, value]) => value !== ""
    ).length;

    const fetchPlants = useCallback((currentFilters: Filters) => {
        setLoading(true);
        setError(null);

        const params: Record<string, string> = {};
        for (const [key, value] of Object.entries(currentFilters)) {
            if (value) {
                params[key] = value;
            }
        }

        api.getPlants(params)
            .then((data: { plants: Plant[] }) => {
                setPlants(data.plants || []);
            })
            .catch((err: Error) => {
                console.error("Error fetching plants:", err);
                setError(err.message);
            })
            .finally(() => {
                setLoading(false);
            });
    }, []);

    useEffect(() => {
        fetchPlants(filters);
    }, [filters, fetchPlants]);

    const handleSearchChange = (value: string) => {
        setSearchInput(value);
        if (debounceRef.current) {
            clearTimeout(debounceRef.current);
        }
        debounceRef.current = setTimeout(() => {
            setFilters((prev) => ({ ...prev, search: value }));
        }, 300);
    };

    const handleFilterChange = (key: keyof Filters, value: string) => {
        setFilters((prev) => ({ ...prev, [key]: value }));
    };

    const handleCheckboxChange = (key: "containers" | "greenhouse") => {
        setFilters((prev) => ({
            ...prev,
            [key]: prev[key] === "true" ? "" : "true",
        }));
    };

    const clearFilters = () => {
        setFilters(DEFAULT_FILTERS);
        setSearchInput("");
    };

    return (
        <>
            {/* Hero */}
            <div className={styles.hero}>
                <h1 className={styles.heroTitle}>Discover Your Perfect Plants</h1>
                <p className={styles.heroSubtitle}>
                    Browse 120+ plants with growing guides, companion tips, and care advice
                </p>
            </div>

            {/* Floating search */}
            <div className={styles.searchSection}>
                <div className={styles.searchBar}>
                    <svg
                        className={styles.searchIcon}
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                    >
                        <circle cx="11" cy="11" r="8" />
                        <line x1="21" y1="21" x2="16.65" y2="16.65" />
                    </svg>
                    <input
                        type="text"
                        placeholder="Search plants by name..."
                        value={searchInput}
                        onChange={(e) => handleSearchChange(e.target.value)}
                        className={styles.searchInput}
                    />
                </div>
            </div>

            <div className={styles.container}>
                {/* Filter toggle */}
                <div className={styles.filterToggleRow}>
                    <button
                        className={styles.filterToggleBtn}
                        onClick={() => setFiltersOpen((prev) => !prev)}
                        type="button"
                    >
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <line x1="4" y1="6" x2="20" y2="6" />
                            <line x1="8" y1="12" x2="20" y2="12" />
                            <line x1="12" y1="18" x2="20" y2="18" />
                        </svg>
                        Filters
                        {activeFilterCount > 0 && (
                            <span className={styles.filterBadge}>
                                {activeFilterCount}
                            </span>
                        )}
                        <svg
                            className={`${styles.chevron} ${filtersOpen ? styles.chevronOpen : ""}`}
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                        >
                            <polyline points="6 9 12 15 18 9" />
                        </svg>
                    </button>
                    {activeFilterCount > 0 && (
                        <button
                            className={styles.clearBtn}
                            onClick={clearFilters}
                            type="button"
                        >
                            Clear Filters
                        </button>
                    )}

                    <span className={styles.resultCount}>
                        {loading
                            ? "Searching..."
                            : `${plants.length} plant${plants.length !== 1 ? "s" : ""} found`}
                    </span>
                </div>

                {error && <p className={styles.error}>{error}</p>}

                <div className={styles.layout}>
                    <aside
                        className={`${styles.filterPanel} ${filtersOpen ? styles.filterPanelOpen : ""}`}
                    >
                        <div className={styles.filterGroup}>
                            <label className={styles.filterLabel}>Sunlight</label>
                            <select
                                className={styles.filterSelect}
                                value={filters.sunlight}
                                onChange={(e) => handleFilterChange("sunlight", e.target.value)}
                            >
                                <option value="">All</option>
                                {SUNLIGHT_OPTIONS.map((opt) => (
                                    <option key={opt} value={opt}>{opt}</option>
                                ))}
                            </select>
                        </div>

                        <div className={styles.filterGroup}>
                            <label className={styles.filterLabel}>Water Needs</label>
                            <select
                                className={styles.filterSelect}
                                value={filters.water_needs}
                                onChange={(e) => handleFilterChange("water_needs", e.target.value)}
                            >
                                <option value="">All</option>
                                {WATER_OPTIONS.map((opt) => (
                                    <option key={opt} value={opt}>{opt}</option>
                                ))}
                            </select>
                        </div>

                        <div className={styles.filterGroup}>
                            <label className={styles.filterLabel}>Growing Season</label>
                            <select
                                className={styles.filterSelect}
                                value={filters.growing_season}
                                onChange={(e) => handleFilterChange("growing_season", e.target.value)}
                            >
                                <option value="">All</option>
                                {SEASON_OPTIONS.map((opt) => (
                                    <option key={opt} value={opt}>{opt}</option>
                                ))}
                            </select>
                        </div>

                        <div className={styles.filterGroup}>
                            <label className={styles.filterLabel}>Space Required</label>
                            <select
                                className={styles.filterSelect}
                                value={filters.space_required}
                                onChange={(e) => handleFilterChange("space_required", e.target.value)}
                            >
                                <option value="">All</option>
                                {SPACE_OPTIONS.map((opt) => (
                                    <option key={opt} value={opt}>{opt}</option>
                                ))}
                            </select>
                        </div>

                        <div className={styles.filterGroup}>
                            <label className={styles.checkboxLabel}>
                                <input
                                    type="checkbox"
                                    checked={filters.containers === "true"}
                                    onChange={() => handleCheckboxChange("containers")}
                                />
                                Container Friendly
                            </label>
                        </div>

                        <div className={styles.filterGroup}>
                            <label className={styles.checkboxLabel}>
                                <input
                                    type="checkbox"
                                    checked={filters.greenhouse === "true"}
                                    onChange={() => handleCheckboxChange("greenhouse")}
                                />
                                Greenhouse Required
                            </label>
                        </div>
                    </aside>

                    <main className={styles.mainContent}>
                        {!loading && plants.length === 0 && !error && (
                            <div className={styles.emptyState}>
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" width="48" height="48" style={{ color: "var(--text-muted)", opacity: 0.4, marginBottom: "var(--space-md)" }}>
                                    <circle cx="11" cy="11" r="8" />
                                    <line x1="21" y1="21" x2="16.65" y2="16.65" />
                                </svg>
                                <p>No plants found matching your filters.</p>
                                <button
                                    className={styles.clearBtn}
                                    onClick={clearFilters}
                                    type="button"
                                >
                                    Clear All Filters
                                </button>
                            </div>
                        )}

                        <div className={styles.plantGrid}>
                            {loading
                                ? Array.from({ length: 9 }).map((_, i) => (
                                    <div key={i} className={styles.plantCard}>
                                        <div className={styles.plantImageWrapper}>
                                            <div className="skeleton" style={{ width: "100%", height: "100%" }} />
                                        </div>
                                        <div className={styles.plantCardBody}>
                                            <div className="skeleton" style={{ height: "1.2rem", width: "70%" }} />
                                            <div className="skeleton" style={{ height: "0.8rem", width: "90%" }} />
                                        </div>
                                    </div>
                                ))
                                : plants.map((plant) => (
                                    <PlantCard key={plant.id} plant={plant} />
                                ))}
                        </div>
                    </main>
                </div>
            </div>
        </>
    );
};

const PlantCard = ({ plant }: { plant: Plant }) => {
    const [imgError, setImgError] = useState(false);

    return (
        <Link
            to={`/plants/${plant.id}`}
            className={styles.plantCardLink}
        >
            <div className={styles.plantCard}>
                <div className={styles.plantImageWrapper}>
                    {plant.imageUrl && !imgError ? (
                        <img
                            src={plant.imageUrl}
                            alt={plant.name}
                            className={styles.plantImage}
                            loading="lazy"
                            onError={() => setImgError(true)}
                        />
                    ) : (
                        <div className={styles.plantImagePlaceholder}>
                            <svg
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                strokeWidth="1.5"
                                className={styles.placeholderIcon}
                            >
                                <path d="M7 20h10" />
                                <path d="M12 20v-6" />
                                <path d="M12 14c-3 0-5.5-2.5-5.5-5.5C6.5 5 9 3 12 3s5.5 2 5.5 5.5C17.5 11.5 15 14 12 14z" />
                            </svg>
                        </div>
                    )}
                </div>
                <div className={styles.plantCardBody}>
                    <h3 className={styles.plantName}>
                        {plant.name}
                    </h3>
                    <div className={styles.plantTags}>
                        {plant.growingSeason && plant.growingSeason !== "N/A" && (
                            <span className={`${styles.tag} ${styles.tagSeason}`}>
                                {plant.growingSeason}
                            </span>
                        )}
                        {plant.sunlight && plant.sunlight !== "N/A" && (
                            <span className={`${styles.tag} ${styles.tagSunlight}`}>
                                {plant.sunlight}
                            </span>
                        )}
                        {plant.waterNeeds && plant.waterNeeds !== "N/A" && (
                            <span className={`${styles.tag} ${styles.tagWater}`}>
                                {plant.waterNeeds} Water
                            </span>
                        )}
                        {plant.spaceRequired && plant.spaceRequired !== "N/A" && (
                            <span className={`${styles.tag} ${styles.tagSpace}`}>
                                {plant.spaceRequired}
                            </span>
                        )}
                    </div>
                </div>
            </div>
        </Link>
    );
};

export default Home;
