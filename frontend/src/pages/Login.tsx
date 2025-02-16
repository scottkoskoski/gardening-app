import { useState, useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import { useNavigate, Link } from "react-router-dom";

const API_BASE_URL = "http://127.0.0.1:5000";

const Login = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState<string | null>(null);
    const auth = useContext(AuthContext);
    const navigate = useNavigate();

    if (!auth) {
        return <p>Loading...</p>;
    }

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);

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
            navigate("/"); // Redirect to home after login
        } catch (err: any) {
            setError(err?.message || "Something went wrong. Please try again.");
        }
    };

    return (
        <div>
            <h2>Login</h2>
            {error && <p style={{ color: "red" }}>{error}</p>}
            <form onSubmit={handleLogin}>
                <label>Username:</label>
                <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                />

                <label>Password:</label>
                <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />

                <button type="submit">Login</button>
            </form>

            <p>
                <Link to="/">Back to Home</Link>
            </p>
            <p>
                Don't have an account? <Link to="/register">Register here</Link>
            </p>
        </div>
    );
};

export default Login;
