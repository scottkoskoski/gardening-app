import { useContext } from "react";
import { Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import styles from "./Navbar.module.css";

const Navbar = () => {
    const auth = useContext(AuthContext);

    if (!auth) return null;

    return (
        <nav className={styles.navbar}>
            <div className={styles.navLinks}>
                <Link to="/" className={styles.link}>
                    Home
                </Link>
                {auth.isAuthenticated() ? (
                    <button
                        onClick={auth.logout}
                        className={styles.logoutButton}
                    >
                        Logout
                    </button>
                ) : (
                    <Link to="/login" className={styles.link}>
                        Login
                    </Link>
                )}
            </div>
        </nav>
    );
};

export default Navbar;
