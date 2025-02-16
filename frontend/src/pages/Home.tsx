import { useEffect, useState } from "react";
import { getPlants } from "../services/api";
import styles from "../styles/Home.module.css";

type Plant = {
    id: number;
    name: string;
    description: string;
};

const Home = () => {
    const [plants, setPlants] = useState<Plant[]>([]);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        getPlants()
            .then((data) => {
                console.log("Fetched plant data:", data); // Debugging log
                setPlants(data.plants || []);
            })
            .catch((error) => {
                console.error("Error fetching plants:", error);
                setError(error.message);
            });
    }, []);

    return (
        <div className={styles.container}>
            <h1>Welcome to my Gardening App!</h1>
            {error && <p style={{ color: "red" }}>{error}</p>}
            <ul className={styles.plantList}>
                {plants.map((plant) => (
                    <li key={plant.id} className={styles.plantItem}>
                        <h2 className={styles.plantName}>{plant.name}</h2>
                        <p className={styles.plantDescription}>
                            {plant.description}
                        </p>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default Home;
