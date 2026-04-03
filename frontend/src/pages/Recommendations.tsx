import { useState, useEffect, useContext } from "react";
import { Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import api from "../services/api";
import styles from "../styles/Recommendations.module.css";

type PlantRecommendation = {
    plant_id: number;
    name: string;
    scientific_name: string | null;
    image_url: string | null;
    description: string | null;
    score: number;
    max_score: number;
    reasons: string[];
    warnings: string[];
    growing_season: string | null;
    sunlight: string | null;
    water_needs: string | null;
    space_required: string | null;
    activity?: string;
};

type RecommendationsResponse = {
    recommendations: PlantRecommendation[];
    zone: string;
    season: string;
};

type SeasonalResponse = {
    seasonal: PlantRecommendation[];
    zone: string;
    season: string;
    month: string;
};

const Recommendations = () => {
    const auth = useContext(AuthContext);
    const token = auth?.isAuthenticated
        ? localStorage.getItem("token") ?? undefined
        : undefined;

    const [recommendations, setRecommendations] = useState<PlantRecommendation[]>([]);
    const [seasonal, setSeasonal] = useState<PlantRecommendation[]>([]);
    const [zone, setZone] = useState<string>("");
    const [season, setSeason] = useState<string>("");
    const [month, setMonth] = useState<string>("");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [profileIncomplete, setProfileIncomplete] = useState(false);

    useEffect(() => {
        const fetchData = async () => {
            if (!token) {
                setLoading(false);
                return;
            }

            try {
                const [recResponse, seasonalResponse] = await Promise.allSettled([
                    api.getRecommendations(token) as Promise<RecommendationsResponse>,
                    api.getSeasonalRecommendations(token) as Promise<SeasonalResponse>,
                ]);

                if (recResponse.status === "fulfilled") {
                    setRecommendations(recResponse.value.recommendations);
                    setZone(recResponse.value.zone);
                    setSeason(recResponse.value.season);
                } else {
                    // Check if profile incomplete
                    setProfileIncomplete(true);
                }

                if (seasonalResponse.status === "fulfilled") {
                    setSeasonal(seasonalResponse.value.seasonal);
                    if (!month) setMonth(seasonalResponse.value.month);
                }
            } catch (err: any) {
                console.error("Error loading recommendations:", err);
                setError("Failed to load recommendations.");
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [token]);

    const scoreColor = (score: number, maxScore: number) => {
        const pct = (score / maxScore) * 100;
        if (pct >= 75) return "#2e7d32";
        if (pct >= 50) return "#f9a825";
        return "#e65100";
    };

    if (loading) {
        return (
            <>
                <div className={styles.pageHeader}>
                    <h1 className={styles.pageTitle}>Recommended for You</h1>
                    <p className={styles.pageSubtitle}>Personalized plant suggestions for your garden</p>
                </div>
                <div className={styles.container}>
                    <div className="skeleton" style={{ height: "1.5rem", width: "200px", marginBottom: "var(--space-lg)" }} />
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "var(--space-md)" }}>
                        {[1, 2, 3].map((i) => (
                            <div key={i} className="skeleton" style={{ height: "80px", borderRadius: "var(--radius-lg)" }} />
                        ))}
                    </div>
                </div>
            </>
        );
    }

    if (profileIncomplete) {
        return (
            <>
                <div className={styles.pageHeader}>
                    <h1 className={styles.pageTitle}>Recommended for You</h1>
                    <p className={styles.pageSubtitle}>Personalized plant suggestions for your garden</p>
                </div>
                <div className={styles.container}>
                    <div className={styles.profilePrompt}>
                        <h2>Complete Your Profile</h2>
                        <p>
                            We need your ZIP code and hardiness zone to provide
                            personalized plant recommendations.
                        </p>
                        <Link to="/profile" className={styles.profileLink}>
                            Go to Profile
                        </Link>
                    </div>
                </div>
            </>
        );
    }

    return (
        <>
        <div className={styles.pageHeader}>
            <h1 className={styles.pageTitle}>Recommended for You</h1>
            <p className={styles.pageSubtitle}>
                Personalized plant suggestions for your garden
                {zone ? ` in Zone ${zone}` : ""}
            </p>
            {zone && <span className={styles.zoneBadge}>Zone {zone}</span>}
        </div>
        <div className={styles.container}>

            {error && <p className={styles.errorMessage}>{error}</p>}

            {/* Seasonal section */}
            {seasonal.length > 0 && (
                <>
                    <h2 className={styles.sectionTitle}>
                        Plant Now — {month || season}
                    </h2>
                    <div className={styles.seasonalGrid}>
                        {seasonal.map((plant) => (
                            <SeasonalCard key={plant.plant_id} plant={plant} />
                        ))}
                    </div>
                </>
            )}

            {/* Main recommendations */}
            <h2 className={styles.sectionTitle}>Personalized Recommendations</h2>
            {recommendations.length > 0 ? (
                <div className={styles.recGrid}>
                    {recommendations.map((plant) => (
                        <RecPlantCard
                            key={plant.plant_id}
                            plant={plant}
                            scoreColor={scoreColor}
                        />
                    ))}
                </div>
            ) : (
                <div className={styles.emptyState}>
                    <p>No recommendations available yet. Check back soon!</p>
                </div>
            )}
        </div>
        </>
    );
};

const PlaceholderIcon = () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" width="32" height="32" style={{ opacity: 0.5 }}>
        <path d="M7 20h10" />
        <path d="M12 20v-6" />
        <path d="M12 14c-3 0-5.5-2.5-5.5-5.5C6.5 5 9 3 12 3s5.5 2 5.5 5.5C17.5 11.5 15 14 12 14z" />
    </svg>
);

const SeasonalCard = ({ plant }: { plant: PlantRecommendation }) => {
    const [imgError, setImgError] = useState(false);

    return (
        <Link
            to={`/plants/${plant.plant_id}`}
            className={styles.seasonalCard}
        >
            {plant.image_url && !imgError ? (
                <img
                    src={plant.image_url}
                    alt={plant.name}
                    className={styles.seasonalImage}
                    onError={() => setImgError(true)}
                />
            ) : (
                <div className={styles.seasonalImagePlaceholder}>
                    <PlaceholderIcon />
                </div>
            )}
            <div className={styles.seasonalInfo}>
                <h4>{plant.name}</h4>
                {plant.activity && (
                    <span
                        className={`${styles.activityBadge} ${
                            plant.activity === "Start indoors"
                                ? styles.indoor
                                : ""
                        }`}
                    >
                        {plant.activity}
                    </span>
                )}
            </div>
        </Link>
    );
};

const RecPlantCard = ({
    plant,
    scoreColor,
}: {
    plant: PlantRecommendation;
    scoreColor: (score: number, maxScore: number) => string;
}) => {
    const [imgError, setImgError] = useState(false);
    const pct = Math.round((plant.score / plant.max_score) * 100);

    return (
        <div className={styles.plantCard}>
            <div className={styles.plantImageWrapper}>
                {plant.image_url && !imgError ? (
                    <img
                        src={plant.image_url}
                        alt={plant.name}
                        className={styles.plantImage}
                        onError={() => setImgError(true)}
                    />
                ) : (
                    <div className={styles.plantImagePlaceholder}>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" width="48" height="48" style={{ opacity: 0.4 }}>
                            <path d="M7 20h10" />
                            <path d="M12 20v-6" />
                            <path d="M12 14c-3 0-5.5-2.5-5.5-5.5C6.5 5 9 3 12 3s5.5 2 5.5 5.5C17.5 11.5 15 14 12 14z" />
                        </svg>
                    </div>
                )}
                <div className={styles.scoreBadge}>
                    {pct}% match
                </div>
            </div>

            <div className={styles.plantBody}>
                <h3 className={styles.plantName}>{plant.name}</h3>
                {plant.scientific_name && (
                    <p className={styles.scientificName}>
                        {plant.scientific_name}
                    </p>
                )}

                <div className={styles.scoreBarWrapper}>
                    <div className={styles.scoreBarTrack}>
                        <div
                            className={styles.scoreBarFill}
                            style={{
                                width: `${pct}%`,
                                backgroundColor: scoreColor(
                                    plant.score,
                                    plant.max_score
                                ),
                            }}
                        />
                    </div>
                    <div className={styles.scoreBarLabel}>
                        {plant.score}/{plant.max_score} pts
                    </div>
                </div>

                <ul className={styles.matchList}>
                    {plant.reasons.map((r, i) => (
                        <li key={`r-${i}`} className={styles.reason}>
                            {r}
                        </li>
                    ))}
                    {plant.warnings.map((w, i) => (
                        <li key={`w-${i}`} className={styles.warning}>
                            {w}
                        </li>
                    ))}
                </ul>

                <div className={styles.growingDetails}>
                    {plant.growing_season && (
                        <span className={styles.detailTag}>
                            {plant.growing_season}
                        </span>
                    )}
                    {plant.sunlight && (
                        <span className={styles.detailTag}>
                            {plant.sunlight}
                        </span>
                    )}
                    {plant.water_needs && (
                        <span className={styles.detailTag}>
                            Water: {plant.water_needs}
                        </span>
                    )}
                    {plant.space_required && (
                        <span className={styles.detailTag}>
                            Space: {plant.space_required}
                        </span>
                    )}
                </div>

                <div className={styles.cardActions}>
                    <Link
                        to={`/plants/${plant.plant_id}`}
                        className={styles.viewButton}
                    >
                        View Details
                    </Link>
                    <Link
                        to="/gardens"
                        className={styles.gardenButton}
                    >
                        Add to Garden
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default Recommendations;
