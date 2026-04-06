import { useState, useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import { useNavigate, Link } from "react-router-dom";
import GoogleSignInButton from "../components/GoogleSignInButton";
import styles from "../styles/Login.module.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000";

const Login = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const auth = useContext(AuthContext);
    const navigate = useNavigate();

    if (!auth) {
        return <p>Loading...</p>;
    }

    const validateInputs = () => {
        if (!username.trim()) {
            setError("Username is required.");
            return false;
        }
        if (!password.trim()) {
            setError("Password is required.");
            return false;
        }
        if (password.length < 6) {
            setError("Password must be at least 6 characters.");
            return false;
        }
        return true;
    };

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);

        if (!validateInputs()) return;

        setLoading(true);

        try {
            const response = await fetch(`${API_BASE_URL}/api/users/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Login failed");
            }

            auth.login(data.token);
            navigate("/dashboard"); // Redirect to dashboard after login
        } catch (err: any) {
            setError(err?.message || "Something went wrong. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.pageWrapper}>
            <div className={styles["login-container"]}>
                <h2>Welcome Back</h2>
                <p className={styles.subtitle}>Sign in to manage your gardens</p>
                {error && <p className={styles["error-message"]}>{error}</p>}
                <form onSubmit={handleLogin} className={styles["login-form"]}>
                    <label htmlFor="login-username">Username</label>
                    <input
                        id="login-username"
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        placeholder="Enter your username"
                        required
                    />

                    <label htmlFor="login-password">Password</label>
                    <input
                        id="login-password"
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Enter your password"
                        required
                    />

                    <button
                        type="submit"
                        className={styles["login-button"]}
                        disabled={loading}
                    >
                        {loading ? "Signing in..." : "Sign In"}
                    </button>
                </form>

                <div className={styles.divider}>
                    <span>or</span>
                </div>

                <div className={styles.googleButtonWrapper}>
                    <GoogleSignInButton
                        onError={(msg) => setError(msg)}
                        text="signin_with"
                    />
                </div>

                <div className={styles.linkContainer}>
                    <p>
                        Don't have an account?{" "}
                        <Link to="/register">Create one</Link>
                    </p>
                    <p>
                        <Link to="/">Back to Plant Catalog</Link>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Login;
