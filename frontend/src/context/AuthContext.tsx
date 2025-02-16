import { createContext, useState, useEffect, ReactNode } from "react";

type AuthContextType = {
    token: string | null;
    login: (token: string) => void;
    logout: () => void;
    isAuthenticated: () => boolean;
};

export const AuthContext = createContext<AuthContextType | undefined>(
    undefined
);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
    const [token, setToken] = useState<string | null>(
        localStorage.getItem("token")
    );

    useEffect(() => {
        if (token) {
            localStorage.setItem("token", token);
        } else {
            localStorage.removeItem("token");
        }
    }, [token]);

    const login = (newToken: string) => {
        setToken(newToken);
    };

    const logout = () => {
        setToken(null);
    };

    return (
        <AuthContext.Provider
            value={{ token, login, logout, isAuthenticated: () => !!token }}
        >
            {children}
        </AuthContext.Provider>
    );
};

export default AuthProvider;
