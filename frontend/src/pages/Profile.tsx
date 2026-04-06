import { useState, useEffect, useContext } from "react";
import styles from "../styles/Profile.module.css";
import { AuthContext } from "../context/AuthContext";
import api from "../services/api";

const Profile = () => {
    const auth = useContext(AuthContext);
    const token = auth?.isAuthenticated
        ? localStorage.getItem("token") ?? undefined
        : undefined;

    const [profile, setProfile] = useState({
        zipCode: "",
        plantHardinessZone: "",
        city: "",
        state: "",
        hasIrrigation: false,
        sunlightHours: null as number | null,
        soilPh: null as number | null,
    });

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    // Fetch plant hardiness zone from backend API
    const fetchHardinessZone = async (zip: string) => {
        try {
            const response = await api.get(
                `/hardiness/get_hardiness_zone?zip=${zip}`
            );
            if (response.zone) {
                setProfile((prev) => ({
                    ...prev,
                    plantHardinessZone: response.zone,
                }));
            }
        } catch (error) {
            console.error("Error fetching hardiness zone:", error);
        }
    };

    // Handle input changes
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value, type, checked } = e.target;
        const newValue = type === "checkbox" ? checked : value;
        setProfile((prev) => ({ ...prev, [name]: newValue }));

        // Fetch plant hardiness zone when zip code changes
        if (name === "zipCode" && value.length === 5) {
            fetchHardinessZone(value);
        }
    };

    // Fetch profile on mount
    useEffect(() => {
        const fetchProfile = async () => {
            if (!token) {
                setLoading(false);
                return;
            }

            try {
                const response = await api.get("/users/profile", token);

                if (response.error) {
                    console.warn(
                        "Profile not found, initializing empty profile."
                    );
                } else {
                    setProfile({
                        zipCode: response.zip_code || "",
                        plantHardinessZone: response.plant_hardiness_zone || "",
                        city: response.city || "",
                        state: response.state || "",
                        hasIrrigation: response.has_irrigation || false,
                        sunlightHours: response.sunlight_hours,
                        soilPh: response.soil_ph,
                    });
                }
            } catch (error) {
                console.error("Error fetching profile:", error);
                setError("Failed to fetch profile. Try again later.");
            } finally {
                setLoading(false);
            }
        };

        fetchProfile();
    }, [token]);

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setError("");
        setSuccess("");

        try {
            await api.post(
                "users/profile",
                {
                    zip_code: profile.zipCode,
                    city: profile.city,
                    state: profile.state,
                    has_irrigation: profile.hasIrrigation,
                    sunlight_hours: profile.sunlightHours,
                    soil_ph: profile.soilPh,
                },
                token
            );

            setSuccess("Profile saved successfully!");
            setTimeout(() => setSuccess(""), 3000);
        } catch (error) {
            console.error("Error saving profile:", error);
            setError("Error saving profile. Please try again.");
        }
    };

    if (loading) {
        return (
            <>
                <div className={styles.pageHeader}>
                    <h1 className={styles.pageTitle}>Your Profile</h1>
                    <p className={styles.pageSubtitle}>Manage your garden preferences</p>
                </div>
                <div className={styles.profileContainer}>
                    <div className={styles.profileCard}>
                        <div className="skeleton" style={{ height: "1.5rem", width: "60%", margin: "0 auto var(--space-xl)" }} />
                        <div className="skeleton" style={{ height: "2.5rem", width: "100%", marginBottom: "var(--space-md)" }} />
                        <div className="skeleton" style={{ height: "2.5rem", width: "100%", marginBottom: "var(--space-md)" }} />
                        <div className="skeleton" style={{ height: "2.5rem", width: "100%" }} />
                    </div>
                </div>
            </>
        );
    }

    return (
        <>
            <div className={styles.pageHeader}>
                <h1 className={styles.pageTitle}>Your Profile</h1>
                <p className={styles.pageSubtitle}>Manage your garden preferences</p>
            </div>
            <div className={styles.profileContainer}>
                <div className={styles.profileCard}>
                    {error && <p className={styles.errorMessage}>{error}</p>}
                    {success && <p className={styles.successMessage}>{success}</p>}

                    <form onSubmit={handleSubmit} className={styles.profileForm}>
                        <h3 className={styles.sectionLabel}>Location</h3>

                        <div className={styles.formGroup}>
                            <label htmlFor="zipCode">ZIP Code</label>
                            <input
                                type="text"
                                id="zipCode"
                                name="zipCode"
                                value={profile.zipCode}
                                onChange={handleChange}
                                required
                                pattern="\d{5}(-\d{4})?"
                                placeholder="e.g. 10001"
                            />
                        </div>

                        <div className={styles.formRow}>
                            <div className={styles.formGroup}>
                                <label htmlFor="city">City</label>
                                <input
                                    type="text"
                                    id="city"
                                    name="city"
                                    value={profile.city || ""}
                                    onChange={handleChange}
                                    placeholder="e.g. Portland"
                                />
                            </div>

                            <div className={styles.formGroup}>
                                <label htmlFor="state">State</label>
                                <input
                                    type="text"
                                    id="state"
                                    name="state"
                                    value={profile.state || ""}
                                    onChange={handleChange}
                                    placeholder="e.g. OR"
                                />
                            </div>
                        </div>

                        {profile.plantHardinessZone && (
                            <div className={styles.formGroup}>
                                <label>Hardiness Zone</label>
                                <div>
                                    <span className={styles.zoneBadge}>
                                        Zone {profile.plantHardinessZone}
                                    </span>
                                </div>
                            </div>
                        )}

                        <hr className={styles.sectionDivider} />
                        <h3 className={styles.sectionLabel}>Garden Conditions</h3>

                        <label className={styles.checkboxLabel}>
                            <input
                                type="checkbox"
                                name="hasIrrigation"
                                checked={profile.hasIrrigation || false}
                                onChange={handleChange}
                            />
                            Has Irrigation System
                        </label>

                        <div className={styles.formRow}>
                            <div className={styles.formGroup}>
                                <label htmlFor="sunlightHours">Daily Sunlight Hours</label>
                                <input
                                    type="number"
                                    id="sunlightHours"
                                    name="sunlightHours"
                                    value={
                                        profile.sunlightHours === null
                                            ? ""
                                            : profile.sunlightHours
                                    }
                                    onChange={handleChange}
                                    min="0"
                                    max="24"
                                    step="0.5"
                                    placeholder="e.g. 6"
                                />
                            </div>

                            <div className={styles.formGroup}>
                                <label htmlFor="soilPh">Soil pH</label>
                                <input
                                    type="number"
                                    id="soilPh"
                                    name="soilPh"
                                    value={profile.soilPh === null ? "" : profile.soilPh}
                                    onChange={handleChange}
                                    min="0"
                                    max="14"
                                    step="0.1"
                                    placeholder="e.g. 6.5"
                                />
                            </div>
                        </div>

                        <button type="submit" className={styles.profileButton}>
                            Save Profile
                        </button>
                    </form>
                </div>
            </div>
        </>
    );
};

export default Profile;
