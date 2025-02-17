import { useContext } from "react";
import { Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import styles from "../styles/Navbar.module.css";

const Navbar = () => {
    const auth = useContext(AuthContext);

    if (!auth) return null;

    return (
        <nav className={styles["navbar"]}>
            <div className={styles["nav-links"]}>
                <Link to="/">Home</Link>
                {auth.isAuthenticated && <Link to="/profile">Profile</Link>}
                {auth.isAuthenticated ? (
                    <button
                        onClick={auth.logout}
                        className={styles["logout-button"]}
                    >
                        Logout
                    </button>
                ) : (
                    <Link to="/login">Login</Link>
                )}
            </div>
        </nav>
    );
};

export default Navbar;
