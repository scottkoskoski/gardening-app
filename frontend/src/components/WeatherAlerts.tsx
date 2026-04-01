import { useState, useEffect } from "react";
import api from "../services/api";
import styles from "../styles/WeatherAlerts.module.css";

type Alert = {
    id: string;
    type: string;
    severity: "critical" | "warning" | "info" | "positive";
    title: string;
    message: string;
    affected_plants: string[];
    action: string;
};

type WeatherAlertsResponse = {
    alerts: Alert[];
    current_conditions: {
        temperature: number;
        precipitation: number;
        description: string;
    };
};

type WeatherAlertsProps = {
    token: string;
};

const DISMISSED_KEY = "weatherAlertsDismissed";

function getDismissedIds(): Set<string> {
    try {
        const raw = sessionStorage.getItem(DISMISSED_KEY);
        if (raw) {
            return new Set(JSON.parse(raw));
        }
    } catch {
        // ignore parse errors
    }
    return new Set();
}

function saveDismissedIds(ids: Set<string>) {
    sessionStorage.setItem(DISMISSED_KEY, JSON.stringify([...ids]));
}

const severityLabel: Record<string, string> = {
    critical: "Critical",
    warning: "Warning",
    info: "Info",
    positive: "Good",
};

const alertStyleMap: Record<string, string> = {
    critical: styles.alertCritical,
    warning: styles.alertWarning,
    info: styles.alertInfo,
    positive: styles.alertPositive,
};

const badgeStyleMap: Record<string, string> = {
    critical: styles.badgeCritical,
    warning: styles.badgeWarning,
    info: styles.badgeInfo,
    positive: styles.badgePositive,
};

const WeatherAlerts = ({ token }: WeatherAlertsProps) => {
    const [alerts, setAlerts] = useState<Alert[]>([]);
    const [dismissed, setDismissed] = useState<Set<string>>(getDismissedIds);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAlerts = async () => {
            try {
                const data: WeatherAlertsResponse = await api.getWeatherAlerts(token);
                setAlerts(data.alerts || []);
            } catch {
                console.warn("Could not fetch weather alerts");
            } finally {
                setLoading(false);
            }
        };

        fetchAlerts();
    }, [token]);

    const handleDismiss = (alertId: string) => {
        const next = new Set(dismissed);
        next.add(alertId);
        setDismissed(next);
        saveDismissedIds(next);
    };

    const visibleAlerts = alerts.filter((a) => !dismissed.has(a.id));

    if (loading) {
        return <div className={styles.loading}>Checking weather alerts...</div>;
    }

    if (visibleAlerts.length === 0) {
        return null;
    }

    return (
        <div className={styles.alertsContainer}>
            {visibleAlerts.map((alert) => (
                <div
                    key={alert.id}
                    className={`${styles.alert} ${alertStyleMap[alert.severity] || ""}`}
                >
                    <span
                        className={`${styles.severityBadge} ${badgeStyleMap[alert.severity] || ""}`}
                    >
                        {severityLabel[alert.severity] || alert.severity}
                    </span>

                    <div className={styles.alertBody}>
                        <h3 className={styles.alertTitle}>{alert.title}</h3>
                        <p className={styles.alertMessage}>{alert.message}</p>

                        {alert.affected_plants.length > 0 && (
                            <div className={styles.affectedPlants}>
                                {alert.affected_plants.map((plant) => (
                                    <span key={plant} className={styles.plantTag}>
                                        {plant}
                                    </span>
                                ))}
                            </div>
                        )}

                        <p className={styles.alertAction}>{alert.action}</p>
                    </div>

                    <button
                        className={styles.dismissButton}
                        onClick={() => handleDismiss(alert.id)}
                        aria-label={`Dismiss ${alert.title}`}
                    >
                        &times;
                    </button>
                </div>
            ))}
        </div>
    );
};

export default WeatherAlerts;
