import { useState, useEffect, useContext } from "react";
import { Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import api from "../services/api";
import styles from "../styles/SoilGuide.module.css";

type PhRange = {
    min: number;
    max: number;
    ideal: number;
};

type PlantAnalysis = {
    plant_name: string;
    garden_name: string;
    preferred_ph: PhRange;
    status: string;
    ph_difference: number;
    recommendation: string;
};

type Amendment = {
    name: string;
    action: string;
    application: string;
    when: string;
    for_plants?: string[];
};

type SoilRecommendations = {
    soil_ph: number;
    overall_status: string;
    plants: PlantAnalysis[];
    amendments: Amendment[];
    general_tips: string[];
};

type PhGuide = {
    plant_preferences: Record<string, PhRange>;
    default_ph: PhRange;
    amendments: {
        to_raise_ph: Amendment[];
        to_lower_ph: Amendment[];
    };
    general_tips: string[];
};

const STATUS_LABELS: Record<string, string> = {
    optimal: "Optimal",
    acceptable: "Acceptable",
    too_acidic: "Too Acidic",
    too_alkaline: "Too Alkaline",
};

const OVERALL_LABELS: Record<string, string> = {
    optimal: "All plants are happy!",
    acceptable: "Mostly good, minor adjustments possible",
    needs_attention: "Some plants need soil amendments",
    no_plants: "No plants in your gardens yet",
};

function badgeClass(status: string): string {
    switch (status) {
        case "optimal":
            return styles.badgeOptimal;
        case "acceptable":
            return styles.badgeAcceptable;
        case "too_acidic":
            return styles.badgeTooAcidic;
        case "too_alkaline":
            return styles.badgeTooAlkaline;
        default:
            return "";
    }
}

function cardClass(status: string): string {
    switch (status) {
        case "optimal":
            return styles.plantCardOptimal;
        case "acceptable":
            return styles.plantCardAcceptable;
        case "too_acidic":
            return styles.plantCardTooAcidic;
        case "too_alkaline":
            return styles.plantCardTooAlkaline;
        default:
            return "";
    }
}

function overallStatusClass(status: string): string {
    switch (status) {
        case "optimal":
            return styles.statusOptimal;
        case "acceptable":
            return styles.statusAcceptable;
        case "needs_attention":
            return styles.statusNeedsAttention;
        case "no_plants":
            return styles.statusNoPlants;
        default:
            return "";
    }
}

const SoilGuide = () => {
    const auth = useContext(AuthContext);
    const token = auth?.isAuthenticated
        ? localStorage.getItem("token") ?? undefined
        : undefined;

    const [recommendations, setRecommendations] =
        useState<SoilRecommendations | null>(null);
    const [phGuide, setPhGuide] = useState<PhGuide | null>(null);
    const [loading, setLoading] = useState(true);
    const [soilPhMissing, setSoilPhMissing] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const guidePromise = api.getPhGuide() as Promise<PhGuide>;

                if (token) {
                    const [recResult, guideResult] = await Promise.allSettled([
                        api.getSoilRecommendations(token) as Promise<SoilRecommendations>,
                        guidePromise,
                    ]);

                    if (guideResult.status === "fulfilled") {
                        setPhGuide(guideResult.value);
                    }

                    if (recResult.status === "fulfilled") {
                        setRecommendations(recResult.value);
                    } else {
                        setSoilPhMissing(true);
                    }
                } else {
                    const guide = await guidePromise;
                    setPhGuide(guide);
                }
            } catch (err) {
                console.error("Error loading soil data:", err);
                setError("Failed to load soil data.");
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [token]);

    if (loading) {
        return (
            <>
                <div className={styles.pageHeader}>
                    <h1 className={styles.pageTitle}>Soil Amendment Guide</h1>
                    <p className={styles.subtitle}>Optimize your soil pH for healthier plants</p>
                </div>
                <div className={styles.container}>
                    <div className="skeleton" style={{ height: "200px", borderRadius: "var(--radius-xl)", marginBottom: "var(--space-lg)" }} />
                    <div className="skeleton" style={{ height: "120px", borderRadius: "var(--radius-xl)" }} />
                </div>
            </>
        );
    }

    return (
        <>
        <div className={styles.pageHeader}>
            <h1 className={styles.pageTitle}>Soil Amendment Guide</h1>
            <p className={styles.subtitle}>Optimize your soil pH for healthier plants</p>
        </div>
        <div className={styles.container}>

            {error && <p className={styles.errorMessage}>{error}</p>}

            {/* Prompt to set soil pH */}
            {soilPhMissing && (
                <div className={styles.profilePrompt}>
                    <h2>Set Your Soil pH</h2>
                    <p>
                        To get personalized soil amendment recommendations, add
                        your soil pH value to your profile. You can measure it
                        with an inexpensive soil test kit.
                    </p>
                    <Link to="/profile" className={styles.profileLink}>
                        Go to Profile
                    </Link>
                </div>
            )}

            {/* Personalized recommendations section */}
            {recommendations && (
                <>
                    {/* pH Scale Visualization */}
                    <div className={styles.phScaleSection}>
                        <h2>Your Soil pH</h2>
                        <div style={{ textAlign: "center" }}>
                            <div className={styles.phValue}>
                                {recommendations.soil_ph}
                            </div>
                            <div
                                className={`${styles.overallStatus} ${overallStatusClass(recommendations.overall_status)}`}
                            >
                                {OVERALL_LABELS[recommendations.overall_status] ||
                                    recommendations.overall_status}
                            </div>
                        </div>

                        <div className={styles.phScaleWrapper}>
                            <div className={styles.phScaleBar}>
                                <div
                                    className={styles.phMarker}
                                    style={{
                                        left: `${(recommendations.soil_ph / 14) * 100}%`,
                                    }}
                                >
                                    <span className={styles.phMarkerLabel}>
                                        pH {recommendations.soil_ph}
                                    </span>
                                    <span className={styles.phMarkerArrow} />
                                </div>
                            </div>
                            <div className={styles.phScaleLabels}>
                                {Array.from({ length: 15 }, (_, i) => (
                                    <span key={i}>{i}</span>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Plant Analysis */}
                    {recommendations.plants.length > 0 ? (
                        <>
                            <h2 className={styles.sectionTitle}>
                                Plant Analysis
                            </h2>
                            <div className={styles.plantGrid}>
                                {recommendations.plants.map((plant, idx) => (
                                    <div
                                        key={idx}
                                        className={`${styles.plantCard} ${cardClass(plant.status)}`}
                                    >
                                        <div className={styles.plantCardHeader}>
                                            <div>
                                                <div
                                                    className={
                                                        styles.plantName
                                                    }
                                                >
                                                    {plant.plant_name}
                                                </div>
                                                <div
                                                    className={
                                                        styles.gardenLabel
                                                    }
                                                >
                                                    {plant.garden_name}
                                                </div>
                                            </div>
                                            <span
                                                className={`${styles.statusBadge} ${badgeClass(plant.status)}`}
                                            >
                                                {STATUS_LABELS[plant.status] ||
                                                    plant.status}
                                            </span>
                                        </div>

                                        <div className={styles.phRange}>
                                            Preferred pH:{" "}
                                            {plant.preferred_ph.min} -{" "}
                                            {plant.preferred_ph.max} (ideal:{" "}
                                            {plant.preferred_ph.ideal})
                                        </div>

                                        {plant.ph_difference > 0 && (
                                            <div className={styles.phRange}>
                                                Difference from range:{" "}
                                                {plant.ph_difference}
                                            </div>
                                        )}

                                        <div className={styles.recommendation}>
                                            {plant.recommendation}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </>
                    ) : (
                        <div className={styles.emptyState}>
                            <p>
                                No plants in your gardens yet. Add plants to get
                                personalized soil recommendations.
                            </p>
                            <Link to="/gardens" className={styles.gardenLink}>
                                Go to Gardens
                            </Link>
                        </div>
                    )}

                    {/* Amendments */}
                    {recommendations.amendments.length > 0 && (
                        <>
                            <h2 className={styles.sectionTitle}>
                                Recommended Amendments
                            </h2>
                            <div className={styles.amendmentList}>
                                {recommendations.amendments.map(
                                    (amend, idx) => (
                                        <div
                                            key={idx}
                                            className={styles.amendmentCard}
                                        >
                                            <div
                                                className={
                                                    styles.amendmentName
                                                }
                                            >
                                                {amend.name}
                                            </div>
                                            <div
                                                className={
                                                    styles.amendmentAction
                                                }
                                            >
                                                {amend.action}
                                            </div>
                                            <p
                                                className={
                                                    styles.amendmentDetail
                                                }
                                            >
                                                <strong>Application:</strong>{" "}
                                                {amend.application}
                                            </p>
                                            <p
                                                className={
                                                    styles.amendmentDetail
                                                }
                                            >
                                                <strong>When:</strong>{" "}
                                                {amend.when}
                                            </p>
                                            {amend.for_plants &&
                                                amend.for_plants.length > 0 && (
                                                    <div
                                                        className={
                                                            styles.forPlants
                                                        }
                                                    >
                                                        {amend.for_plants.map(
                                                            (p) => (
                                                                <span
                                                                    key={p}
                                                                    className={
                                                                        styles.plantTag
                                                                    }
                                                                >
                                                                    {p}
                                                                </span>
                                                            )
                                                        )}
                                                    </div>
                                                )}
                                        </div>
                                    )
                                )}
                            </div>
                        </>
                    )}

                    {/* General Tips */}
                    <h2 className={styles.sectionTitle}>General Tips</h2>
                    <ul className={styles.tipsList}>
                        {recommendations.general_tips.map((tip, idx) => (
                            <li key={idx}>{tip}</li>
                        ))}
                    </ul>
                </>
            )}

            {/* Reference Section - pH Guide */}
            {phGuide && (
                <div className={styles.referenceSection}>
                    <h2 className={styles.sectionTitle}>
                        pH Preference Reference
                    </h2>
                    <table className={styles.referenceTable}>
                        <thead>
                            <tr>
                                <th>Plant</th>
                                <th>Min pH</th>
                                <th>Max pH</th>
                                <th>Ideal pH</th>
                            </tr>
                        </thead>
                        <tbody>
                            {Object.entries(phGuide.plant_preferences)
                                .sort(([a], [b]) => a.localeCompare(b))
                                .map(([name, pref]) => (
                                    <tr key={name}>
                                        <td>{name}</td>
                                        <td>{pref.min}</td>
                                        <td>{pref.max}</td>
                                        <td>{pref.ideal}</td>
                                    </tr>
                                ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
        </>
    );
};

export default SoilGuide;
