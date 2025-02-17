import { useState } from "react";
import styles from "../styles/Profile.module.css";

const Profile = () => {
    const [profile, setProfile] = useState({
        firstName: "",
        lastName: "",
        zipCode: "",
        gardenType: "",
    });

    const handleChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
    ) => {
        setProfile({
            ...profile,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        console.log("Submitting profile:", profile);
        // TODO: Send data to the backend
    };

    return (
        <div className={styles.profileContainer}>
            <h2 className={styles.profileTitle}>User Profile</h2>
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
                    Garden Type:
                    <select
                        name="gardenType"
                        value={profile.gardenType}
                        onChange={handleChange}
                        required
                    >
                        <option value="">Select a garden type</option>
                        <option value="raised_bed">Raised Bed</option>
                        <option value="container">Container</option>
                        <option value="in_ground">In-Ground</option>
                        <option value="hydroponic">Hydroponic</option>
                    </select>
                </label>
                <button type="submit" className={styles.profileButton}>
                    Save Profile
                </button>
            </form>
        </div>
    );
};

export default Profile;
