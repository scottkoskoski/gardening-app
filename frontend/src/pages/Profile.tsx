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

    // Fetch plant hardiness zone from backend API
    const fetchHardinessZone = async (zip: string) => {
        try {
            const response = await api.get(
                `/hardiness/get_hardiness_zone?zip=${zip}`
            );
            if (response.zone) {
                // Ensure correct response key
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
        const { name, value } = e.target;
        setProfile((prev) => ({ ...prev, [name]: value }));

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
                console.log("Fetching profile with token:", token);
                const response = await api.get("/users/profile", token);
                console.log("Profile response:", response);

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

        console.log("Submitting profile data:", profile);

        try {
            const response = await api.post(
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

            console.log("Profile updated:", response);
            alert("Profile saved successfully!");
        } catch (error) {
            console.error("Error saving profile:", error);
            setError("Error saving profile. Please try again.");
        }
    };

    if (loading) {
        return (
            <div className={styles.profileContainer}>
                <p>Loading...</p>
            </div>
        );
    }

    return (
        <div className={styles.profileContainer}>
            <h2 className={styles.profileTitle}>User Profile</h2>

            {error && <p className={styles.errorMessage}>{error}</p>}

            <form onSubmit={handleSubmit} className={styles.profileForm}>
                <label>
                    Zip Code:
                    <input
                        type="text"
                        name="zipCode"
                        value={profile.zipCode}
                        onChange={handleChange}
                        required
                        pattern="\d{5}(-\d{4})?"
                        placeholder="12345 or 12345-6789"
                    />
                </label>

                <label>
                    City:
                    <input
                        type="text"
                        name="city"
                        value={profile.city || ""}
                        onChange={handleChange}
                    />
                </label>

                <label>
                    State:
                    <input
                        type="text"
                        name="state"
                        value={profile.state || ""}
                        onChange={handleChange}
                    />
                </label>

                <label className={styles.checkboxLabel}>
                    <input
                        type="checkbox"
                        name="hasIrrigation"
                        checked={profile.hasIrrigation || false}
                        onChange={handleChange}
                    />
                    Has Irrigation System
                </label>

                <label>
                    Daily Sunlight Hours:
                    <input
                        type="number"
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
                    />
                </label>

                <label>
                    Soil pH:
                    <input
                        type="number"
                        name="soilPh"
                        value={profile.soilPh === null ? "" : profile.soilPh}
                        onChange={handleChange}
                        min="0"
                        max="14"
                        step="0.1"
                    />
                </label>

                <label>
                    Plant Hardiness Zone:
                    <input
                        type="text"
                        name="plantHardinessZone"
                        value={profile.plantHardinessZone}
                        disabled
                    />
                </label>

                <button type="submit" className={styles.profileButton}>
                    Save Profile
                </button>
            </form>
        </div>
    );
};

export default Profile;
