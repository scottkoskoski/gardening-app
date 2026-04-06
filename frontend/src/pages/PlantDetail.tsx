import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../services/api";
import styles from "../styles/PlantDetail.module.css";

type CompanionData = {
    good: string[];
    bad: string[];
    tips: string;
};

type CareTips = {
    growing_tips: string[];
    common_problems: string[];
    harvesting: string;
    storage: string;
};

type PlantData = {
    id: number;
    name: string;
    scientificName: string | null;
    description: string;
    hardinessMin: string;
    hardinessMax: string;
    bestTemperatureMin: number | null;
    bestTemperatureMax: number | null;
    requiresGreenhouse: boolean;
    suitableForContainers: boolean;
    growingSeason: string;
    waterNeeds: string;
    sunlight: string;
    spaceRequired: string;
    sowingMethod: string;
    spread: number | null;
    rowSpacing: number | null;
    height: number | null;
    imageUrl: string;
    companions: CompanionData;
};

const PlantDetail = () => {
    const { plantId } = useParams<{ plantId: string }>();
    const [plant, setPlant] = useState<PlantData | null>(null);
    const [careTips, setCareTips] = useState<CareTips | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [imageError, setImageError] = useState(false);

    useEffect(() => {
        if (!plantId) return;

        const id = Number(plantId);

        Promise.all([
            api.getPlantDetails(id),
            api.getPlantCareTips(id).catch(() => null),
        ])
            .then(([plantData, tipsData]: [PlantData, { care_tips: CareTips; plant_name: string } | null]) => {
                setPlant(plantData);
                if (tipsData?.care_tips) {
                    setCareTips(tipsData.care_tips);
                }
                setLoading(false);
            })
            .catch((err) => {
                console.error("Error fetching plant details:", err);
                setError(err.message);
                setLoading(false);
            });
    }, [plantId]);

    if (loading) return (
        <div className={styles.container}>
            <div className="skeleton" style={{ height: "0.9rem", width: "140px", marginBottom: "var(--space-lg)" }} />
            <div style={{ display: "flex", gap: "var(--space-2xl)", background: "var(--card-white)", borderRadius: "var(--radius-xl)", padding: "var(--space-xl)", boxShadow: "var(--shadow-md)", border: "1px solid var(--border-light)" }}>
                <div className="skeleton" style={{ width: "320px", height: "260px", borderRadius: "var(--radius-lg)", flexShrink: 0 }} />
                <div style={{ flex: 1 }}>
                    <div className="skeleton" style={{ height: "2rem", width: "60%", marginBottom: "var(--space-md)" }} />
                    <div className="skeleton" style={{ height: "1rem", width: "40%", marginBottom: "var(--space-lg)" }} />
                    <div style={{ display: "flex", gap: "10px" }}>
                        <div className="skeleton" style={{ height: "2rem", width: "120px", borderRadius: "9999px" }} />
                        <div className="skeleton" style={{ height: "2rem", width: "120px", borderRadius: "9999px" }} />
                    </div>
                </div>
            </div>
        </div>
    );
    if (error) return <div className={styles.error}>Error: {error}</div>;
    if (!plant) return <div className={styles.error}>Plant not found.</div>;

    const hasCompanions =
        plant.companions.good.length > 0 || plant.companions.bad.length > 0;

    return (
        <div className={styles.container}>
            <Link to="/" className={styles.backLink}>
                &larr; Back to Plant List
            </Link>

            {/* Hero Section */}
            <div className={styles.hero}>
                {plant.imageUrl && plant.imageUrl !== "N/A" && !imageError ? (
                    <img
                        src={plant.imageUrl}
                        alt={plant.name}
                        className={styles.heroImage}
                        onError={() => setImageError(true)}
                    />
                ) : (
                    <div className={styles.heroImagePlaceholder}>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" width="64" height="64" style={{ opacity: 0.6 }}>
                            <path d="M7 20h10" />
                            <path d="M12 20v-6" />
                            <path d="M12 14c-3 0-5.5-2.5-5.5-5.5C6.5 5 9 3 12 3s5.5 2 5.5 5.5C17.5 11.5 15 14 12 14z" />
                        </svg>
                    </div>
                )}
                <div className={styles.heroInfo}>
                    <h1 className={styles.plantName}>{plant.name}</h1>
                    {plant.scientificName && (
                        <p className={styles.scientificName}>{plant.scientificName}</p>
                    )}
                    <div className={styles.badges}>
                        {plant.requiresGreenhouse && (
                            <span className={`${styles.badge} ${styles.badgeGreenhouse}`}>
                                Greenhouse Required
                            </span>
                        )}
                        {plant.suitableForContainers && (
                            <span className={`${styles.badge} ${styles.badgeContainer}`}>
                                Container Friendly
                            </span>
                        )}
                    </div>
                </div>
            </div>

            {/* Growing Requirements */}
            <div className={styles.section}>
                <h2 className={styles.sectionTitle}>Growing Requirements</h2>
                <div className={styles.detailsGrid}>
                    <div className={styles.detailItem}>
                        <span className={styles.detailLabel}>Sunlight</span>
                        <span className={styles.detailValue}>{plant.sunlight}</span>
                    </div>
                    <div className={styles.detailItem}>
                        <span className={styles.detailLabel}>Water Needs</span>
                        <span className={styles.detailValue}>{plant.waterNeeds}</span>
                    </div>
                    <div className={styles.detailItem}>
                        <span className={styles.detailLabel}>Growing Season</span>
                        <span className={styles.detailValue}>{plant.growingSeason}</span>
                    </div>
                    <div className={styles.detailItem}>
                        <span className={styles.detailLabel}>Space Required</span>
                        <span className={styles.detailValue}>{plant.spaceRequired}</span>
                    </div>
                    <div className={styles.detailItem}>
                        <span className={styles.detailLabel}>Sowing Method</span>
                        <span className={styles.detailValue}>{plant.sowingMethod}</span>
                    </div>
                </div>
            </div>

            {/* Physical Characteristics */}
            {(plant.spread || plant.rowSpacing || plant.height) && (
                <div className={styles.section}>
                    <h2 className={styles.sectionTitle}>Physical Characteristics</h2>
                    <div className={styles.detailsGrid}>
                        {plant.spread && (
                            <div className={styles.detailItem}>
                                <span className={styles.detailLabel}>Spread</span>
                                <span className={styles.detailValue}>{plant.spread} cm</span>
                            </div>
                        )}
                        {plant.rowSpacing && (
                            <div className={styles.detailItem}>
                                <span className={styles.detailLabel}>Row Spacing</span>
                                <span className={styles.detailValue}>{plant.rowSpacing} cm</span>
                            </div>
                        )}
                        {plant.height && (
                            <div className={styles.detailItem}>
                                <span className={styles.detailLabel}>Height</span>
                                <span className={styles.detailValue}>{plant.height} cm</span>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Hardiness Zones */}
            {(plant.hardinessMin !== "N/A" || plant.hardinessMax !== "N/A") && (
                <div className={styles.section}>
                    <h2 className={styles.sectionTitle}>Hardiness Zones</h2>
                    <div className={styles.detailsGrid}>
                        <div className={styles.detailItem}>
                            <span className={styles.detailLabel}>Zone Range</span>
                            <span className={styles.detailValue}>
                                {plant.hardinessMin} - {plant.hardinessMax}
                            </span>
                        </div>
                    </div>
                </div>
            )}

            {/* Temperature Preferences */}
            {(plant.bestTemperatureMin !== null || plant.bestTemperatureMax !== null) && (
                <div className={styles.section}>
                    <h2 className={styles.sectionTitle}>Temperature Preferences</h2>
                    <div className={styles.detailsGrid}>
                        {plant.bestTemperatureMin !== null && (
                            <div className={styles.detailItem}>
                                <span className={styles.detailLabel}>Min Temperature</span>
                                <span className={styles.detailValue}>{plant.bestTemperatureMin}&deg;F</span>
                            </div>
                        )}
                        {plant.bestTemperatureMax !== null && (
                            <div className={styles.detailItem}>
                                <span className={styles.detailLabel}>Max Temperature</span>
                                <span className={styles.detailValue}>{plant.bestTemperatureMax}&deg;F</span>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Companion Planting */}
            <div className={styles.section}>
                <h2 className={styles.sectionTitle}>Companion Planting</h2>
                {hasCompanions ? (
                    <>
                        {plant.companions.good.length > 0 && (
                            <div className={styles.companionGroup}>
                                <div className={styles.companionLabel}>Good Companions</div>
                                <div className={styles.tags}>
                                    {plant.companions.good.map((name) => (
                                        <span key={name} className={styles.tagGood}>
                                            {name}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}
                        {plant.companions.bad.length > 0 && (
                            <div className={styles.companionGroup}>
                                <div className={styles.companionLabel}>Bad Companions</div>
                                <div className={styles.tags}>
                                    {plant.companions.bad.map((name) => (
                                        <span key={name} className={styles.tagBad}>
                                            {name}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}
                        {plant.companions.tips && (
                            <div className={styles.companionTips}>
                                {plant.companions.tips}
                            </div>
                        )}
                    </>
                ) : (
                    <p className={styles.noCompanions}>
                        No companion planting data available for this plant.
                    </p>
                )}
            </div>

            {/* Care Tips */}
            {careTips && (
                <div className={styles.section}>
                    <h2 className={styles.sectionTitle}>Growing Guide</h2>

                    {careTips.growing_tips.length > 0 && (
                        <div className={styles.careGroup}>
                            <h3 className={styles.careSubtitle}>Growing Tips</h3>
                            <ul className={styles.careList}>
                                {careTips.growing_tips.map((tip, i) => (
                                    <li key={i}>{tip}</li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {careTips.common_problems.length > 0 && (
                        <div className={styles.careGroup}>
                            <h3 className={styles.careSubtitle}>Common Problems</h3>
                            <ul className={styles.careList}>
                                {careTips.common_problems.map((problem, i) => (
                                    <li key={i}>{problem}</li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {careTips.harvesting && (
                        <div className={styles.careGroup}>
                            <h3 className={styles.careSubtitle}>Harvesting</h3>
                            <p className={styles.description}>{careTips.harvesting}</p>
                        </div>
                    )}

                    {careTips.storage && (
                        <div className={styles.careGroup}>
                            <h3 className={styles.careSubtitle}>Storage</h3>
                            <p className={styles.description}>{careTips.storage}</p>
                        </div>
                    )}
                </div>
            )}

            {/* Description */}
            {plant.description && (
                <div className={styles.section}>
                    <h2 className={styles.sectionTitle}>About This Plant</h2>
                    <p className={styles.description}>{plant.description}</p>
                </div>
            )}

            {/* Actions */}
            <div className={styles.actions}>
                <Link to="/gardens" className={styles.addToGardenBtn}>
                    Add to Garden
                </Link>
            </div>
        </div>
    );
};

export default PlantDetail;
