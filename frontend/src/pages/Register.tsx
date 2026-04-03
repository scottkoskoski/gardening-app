import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import GoogleSignInButton from "../components/GoogleSignInButton";
import styles from "../styles/Register.module.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const Register = () => {
    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const validateEmail = (email: string) =>
        /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

    const handleRegister = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setSuccess(null);

        // Doing some basic validation
        if (!username || !email || !password) {
            setError("All fields are required.");
            return;
        }

        if (!validateEmail(email)) {
            setError("Please enter a valid email address.");
            return;
        }

        if (password.length < 6) {
            setError("Password must be at least 6 characters long.");
            return;
        }

        setLoading(true);

        try {
            const response = await fetch(`${API_BASE_URL}/api/users/register`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, email, password }), // Send user data
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Registration failed");
            }

            setSuccess("Registration successful! Redirecting to login...");
            setTimeout(() => navigate("/login"), 2000); // Redirect to login after 2 seconds
        } catch (err: any) {
            setError(err?.message || "Something went wrong. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.pageWrapper}>
            <div className={styles["register-container"]}>
                <h2>Create Account</h2>
                <p className={styles.subtitle}>Start growing your dream garden</p>
                {error && <p className={styles["error-message"]}>{error}</p>}
                {success && <p className={styles["success-message"]}>{success}</p>}
                <form onSubmit={handleRegister} className={styles["register-form"]}>
                    <label htmlFor="reg-username">Username</label>
                    <input
                        id="reg-username"
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        placeholder="Choose a username"
                        required
                    />

                    <label htmlFor="reg-email">Email</label>
                    <input
                        id="reg-email"
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="your@email.com"
                        required
                    />

                    <label htmlFor="reg-password">Password</label>
                    <input
                        id="reg-password"
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="At least 6 characters"
                        required
                    />
                    <button
                        type="submit"
                        className={styles["register-button"]}
                        disabled={loading}
                    >
                        {loading ? "Creating account..." : "Create Account"}
                    </button>
                </form>

                <div className={styles.divider}>
                    <span>or</span>
                </div>

                <div className={styles.googleButtonWrapper}>
                    <GoogleSignInButton
                        onError={(msg) => setError(msg)}
                        text="signup_with"
                    />
                </div>

                <div className={styles.linkContainer}>
                    <p>
                        Already have an account? <Link to="/login">Sign in</Link>
                    </p>
                    <p>
                        <Link to="/">Back to Plant Catalog</Link>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Register;
