import {
    createContext,
    useState,
    useEffect,
    ReactNode,
    useContext,
} from "react";

// Defining the expected structure for the AuthContext
interface AuthContextType {
    isAuthenticated: boolean;
    token: string | null;
    login: (token: string) => void;
    logout: () => void;
}

// Export AuthContext so other components can use it
export const AuthContext = createContext<AuthContextType | null>(null);

// Create useAuth hook to access the AuthContext
export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth must e used within an AuthProvider");
    }
    return context;
};

export const AuthProvider = ({ children }: { children: ReactNode }) => {
    const [token, setToken] = useState<string | null>(
        localStorage.getItem("token")
    );

    useEffect(() => {
        const storedToken = localStorage.getItem("token");
        if (storedToken) {
            setToken(storedToken);
        }
    }, []);

    const login = (token: string) => {
        localStorage.setItem("token", token);
        setToken(token);
    };

    const logout = () => {
        localStorage.removeItem("token");
        setToken(null);
    };

    return (
        <AuthContext.Provider
            value={{ isAuthenticated: !!token, token, login, logout }}
        >
            {children}
        </AuthContext.Provider>
    );
};
