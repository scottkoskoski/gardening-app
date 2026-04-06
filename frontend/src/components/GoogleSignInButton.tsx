import { useEffect, useRef, useContext, useState } from "react";
import { AuthContext } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000";
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;

interface GoogleSignInButtonProps {
    onError?: (message: string) => void;
    text?: "signin_with" | "signup_with" | "continue_with" | "signin";
}

const GoogleSignInButton = ({ onError, text = "signin_with" }: GoogleSignInButtonProps) => {
    const buttonRef = useRef<HTMLDivElement>(null);
    const auth = useContext(AuthContext);
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!GOOGLE_CLIENT_ID || !window.google) {
            return;
        }

        window.google.accounts.id.initialize({
            client_id: GOOGLE_CLIENT_ID,
            callback: handleGoogleResponse,
        });

        if (buttonRef.current) {
            window.google.accounts.id.renderButton(buttonRef.current, {
                theme: "outline",
                size: "large",
                text: text,
                shape: "rectangular",
                width: 400,
            });
        }
    }, []);

    const handleGoogleResponse = async (response: CredentialResponse) => {
        if (!response.credential) {
            onError?.("Google sign-in failed. Please try again.");
            return;
        }

        setLoading(true);

        try {
            const res = await fetch(`${API_BASE_URL}/api/users/google-login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ credential: response.credential }),
            });

            const data = await res.json();

            if (!res.ok) {
                throw new Error(data.error || "Google login failed");
            }

            auth?.login(data.token);
            navigate("/dashboard");
        } catch (err: any) {
            onError?.(err?.message || "Google sign-in failed. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    if (!GOOGLE_CLIENT_ID) {
        return null;
    }

    return (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
            {loading && <p style={{ fontSize: "0.875rem", color: "#666" }}>Signing in...</p>}
            <div ref={buttonRef} style={{ display: loading ? "none" : "block" }} />
        </div>
    );
};

export default GoogleSignInButton;
