import { useEffect, useState } from "react";
import { getPlants } from "../services/api";

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
        <div>
            <h1>Welcome to my Gardening App!</h1>
            {error && <p style={{ color: "red" }}>{error}</p>}
            <ul>
                {plants.map((plant) => (
                    <li key={plant.id}>
                        <h2>{plant.name}</h2>
                        <p>{plant.description}</p>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default Home;
