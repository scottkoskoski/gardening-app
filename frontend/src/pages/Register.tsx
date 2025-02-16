import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";

const API_BASE_URL = "http://127.0.0.1:5000";

const Register = () => {
    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);
    const navigate = useNavigate();

    const handleRegister = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setSuccess(null);

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
        }
    };

    return (
        <div>
            <h2>Register</h2>
            {error && <p style={{ color: "red" }}>{error}</p>}
            {success && <p style={{ color: "green" }}>{success}</p>}
            <form onSubmit={handleRegister}>
                <label>Username:</label>
                <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                />

                <label>Email:</label>
                <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                />

                <label>Password:</label>
                <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />
                <button type="submit">Register</button>
            </form>

            <p>
                Already have an account? <Link to="/login">Login here</Link>
            </p>
            <p>
                <Link to="/">Back to home</Link>
            </p>
        </div>
    );
};

export default Register;
