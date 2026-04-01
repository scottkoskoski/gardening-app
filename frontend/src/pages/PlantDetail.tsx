import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../services/api";
import styles from "../styles/PlantDetail.module.css";

type CompanionData = {
    good: string[];
    bad: string[];
    tips: string;
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
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!plantId) return;

        api.getPlantDetails(Number(plantId))
            .then((data: PlantData) => {
                setPlant(data);
                setLoading(false);
            })
            .catch((err) => {
                console.error("Error fetching plant details:", err);
                setError(err.message);
                setLoading(false);
            });
    }, [plantId]);

    if (loading) return <div className={styles.loading}>Loading plant details...</div>;
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
                {plant.imageUrl && plant.imageUrl !== "N/A" ? (
                    <img
                        src={plant.imageUrl}
                        alt={plant.name}
                        className={styles.heroImage}
                    />
                ) : (
                    <div className={styles.heroImagePlaceholder}>
                        &#127793;
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

            {/* Description */}
            {plant.description && (
                <div className={styles.section}>
                    <h2 className={styles.sectionTitle}>Description</h2>
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
