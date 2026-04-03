import { Link } from "react-router-dom";
import styles from "../styles/Footer.module.css";

const Footer = () => {
    return (
        <footer className={styles.footer}>
            <div className={styles.inner}>
                <div className={styles.brand}>
                    <div className={styles.logo}>
                        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M7 20h10" />
                            <path d="M12 20v-8" />
                            <path d="M12 12c-3.5 0-6-2.5-6-6 0-1 .5-2.5 2-3.5C9.5 1.5 11 1 12 1s2.5.5 4 1.5c1.5 1 2 2.5 2 3.5 0 3.5-2.5 6-6 6z" />
                        </svg>
                        <span>GreenThumb</span>
                    </div>
                    <p className={styles.tagline}>
                        Cultivating beautiful gardens, one plant at a time.
                    </p>
                </div>

                <div className={styles.links}>
                    <div className={styles.linkGroup}>
                        <h4 className={styles.linkGroupTitle}>Explore</h4>
                        <Link to="/">Plant Catalog</Link>
                        <Link to="/calendar">Planting Calendar</Link>
                    </div>
                    <div className={styles.linkGroup}>
                        <h4 className={styles.linkGroupTitle}>My Garden</h4>
                        <Link to="/dashboard">Dashboard</Link>
                        <Link to="/gardens">Gardens</Link>
                        <Link to="/tasks">Tasks</Link>
                    </div>
                    <div className={styles.linkGroup}>
                        <h4 className={styles.linkGroupTitle}>Learn</h4>
                        <Link to="/recommendations">Tips</Link>
                        <Link to="/soil">Soil Guide</Link>
                        <Link to="/harvests">Harvests</Link>
                    </div>
                </div>
            </div>

            <div className={styles.bottom}>
                <p>Made with care for gardeners everywhere.</p>
            </div>
        </footer>
    );
};

export default Footer;
