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
            <div className={styles.container}>
                <p className={styles.loading}>Loading recommendations...</p>
            </div>
        );
    }

    if (profileIncomplete) {
        return (
            <div className={styles.container}>
                <div className={styles.header}>
                    <h1 className={styles.pageTitle}>Recommended for You</h1>
                </div>
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
        );
    }

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <h1 className={styles.pageTitle}>Recommended for You</h1>
                {zone && <span className={styles.zoneBadge}>Zone {zone}</span>}
            </div>

            {error && <p className={styles.errorMessage}>{error}</p>}

            {/* Seasonal section */}
            {seasonal.length > 0 && (
                <>
                    <h2 className={styles.sectionTitle}>
                        Plant Now — {month || season}
                    </h2>
                    <div className={styles.seasonalGrid}>
                        {seasonal.map((plant) => (
                            <Link
                                key={plant.plant_id}
                                to={`/plants/${plant.plant_id}`}
                                className={styles.seasonalCard}
                            >
                                {plant.image_url ? (
                                    <img
                                        src={plant.image_url}
                                        alt={plant.name}
                                        className={styles.seasonalImage}
                                    />
                                ) : (
                                    <div className={styles.seasonalImage} />
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
                        ))}
                    </div>
                </>
            )}

            {/* Main recommendations */}
            <h2 className={styles.sectionTitle}>Personalized Recommendations</h2>
            {recommendations.length > 0 ? (
                <div className={styles.recGrid}>
                    {recommendations.map((plant) => {
                        const pct = Math.round(
                            (plant.score / plant.max_score) * 100
                        );
                        return (
                            <div key={plant.plant_id} className={styles.plantCard}>
                                <div className={styles.plantImageWrapper}>
                                    {plant.image_url ? (
                                        <img
                                            src={plant.image_url}
                                            alt={plant.name}
                                            className={styles.plantImage}
                                        />
                                    ) : (
                                        <div className={styles.plantImagePlaceholder}>
                                            🌱
                                        </div>
                                    )}
                                    <div className={styles.scoreBadge}>
                                        {pct}% match
                                    </div>
                                </div>

                                <div className={styles.plantBody}>
                                    <h3 className={styles.plantName}>
                                        {plant.name}
                                    </h3>
                                    {plant.scientific_name && (
                                        <p className={styles.scientificName}>
                                            {plant.scientific_name}
                                        </p>
                                    )}

                                    {/* Score bar */}
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

                                    {/* Reasons and warnings */}
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

                                    {/* Growing details */}
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

                                    {/* Actions */}
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
                    })}
                </div>
            ) : (
                <div className={styles.emptyState}>
                    <p>No recommendations available yet. Check back soon!</p>
                </div>
            )}
        </div>
    );
};

export default Recommendations;
