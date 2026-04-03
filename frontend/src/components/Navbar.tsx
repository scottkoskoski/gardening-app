import { useContext, useState } from "react";
import { Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import styles from "../styles/Navbar.module.css";

const Navbar = () => {
    const auth = useContext(AuthContext);
    const [menuOpen, setMenuOpen] = useState(false);

    if (!auth) return null;

    const closeMenu = () => setMenuOpen(false);

    return (
        <nav className={styles.navbar}>
            <Link to="/" className={styles.brand} onClick={closeMenu}>
                <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M7 20h10" />
                    <path d="M12 20v-8" />
                    <path d="M12 12c-3.5 0-6-2.5-6-6 0-1 .5-2.5 2-3.5C9.5 1.5 11 1 12 1s2.5.5 4 1.5c1.5 1 2 2.5 2 3.5 0 3.5-2.5 6-6 6z" />
                </svg>
                <span>GreenThumb</span>
            </Link>

            <button
                className={styles.hamburger}
                onClick={() => setMenuOpen((prev) => !prev)}
                aria-label="Toggle navigation menu"
                type="button"
            >
                <span className={`${styles.hamburgerLine} ${menuOpen ? styles.open : ""}`} />
                <span className={`${styles.hamburgerLine} ${menuOpen ? styles.open : ""}`} />
                <span className={`${styles.hamburgerLine} ${menuOpen ? styles.open : ""}`} />
            </button>

            <div className={`${styles.navLinks} ${menuOpen ? styles.navLinksOpen : ""}`}>
                <Link to="/" onClick={closeMenu}>Plants</Link>
                <Link to="/calendar" onClick={closeMenu}>Calendar</Link>
                {auth.isAuthenticated && (
                    <>
                        <span className={styles.divider} />
                        <Link to="/dashboard" onClick={closeMenu}>Dashboard</Link>
                        <Link to="/gardens" onClick={closeMenu}>Gardens</Link>
                        <Link to="/recommendations" onClick={closeMenu}>Tips</Link>
                        <Link to="/profile" onClick={closeMenu}>Profile</Link>
                    </>
                )}
                {auth.isAuthenticated ? (
                    <button
                        onClick={() => { auth.logout(); closeMenu(); }}
                        className={styles.logoutButton}
                    >
                        Sign Out
                    </button>
                ) : (
                    <>
                        <span className={styles.divider} />
                        <Link to="/login" onClick={closeMenu} className={styles.loginLink}>Sign In</Link>
                    </>
                )}
            </div>
        </nav>
    );
};

export default Navbar;
