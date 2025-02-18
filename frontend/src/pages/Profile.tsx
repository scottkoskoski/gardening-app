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
        firstName: "",
        lastName: "",
        zipCode: "",
        plantHardinessZone: "",
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
                        firstName: response.first_name || "",
                        lastName: response.last_name || "",
                        zipCode: response.zip_code || "",
                        plantHardinessZone: response.plant_hardiness_zone || "",
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
                "/users/profile",
                {
                    first_name: profile.firstName,
                    last_name: profile.lastName,
                    zip_code: profile.zipCode,
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
                    First Name:
                    <input
                        type="text"
                        name="firstName"
                        value={profile.firstName}
                        onChange={handleChange}
                        required
                    />
                </label>
                <label>
                    Last Name:
                    <input
                        type="text"
                        name="lastName"
                        value={profile.lastName}
                        onChange={handleChange}
                        required
                    />
                </label>
                <label>
                    Zip Code:
                    <input
                        type="text"
                        name="zipCode"
                        value={profile.zipCode}
                        onChange={handleChange}
                        required
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
