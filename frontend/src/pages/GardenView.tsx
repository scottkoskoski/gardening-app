import { useState, useEffect, useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import api from "../services/api";
import styles from "../styles/GardenView.module.css";

// Define types for our data structures
type Plant = {
    id: number;
    name: string;
    scientific_name?: string;
    description?: string;
    image_url?: string;
    water_needs?: string;
    sunlight?: string;
};

type GardenPlant = {
    id: number;
    plant_id: number;
    plant_name: string;
    growth_stage: string;
    expected_harvest_date?: string;
};

type Garden = {
    id: number;
    garden_name: string;
    garden_type: string;
    garden_size?: string;
    water_source?: string;
    soil_type?: string;
    plant_hardiness_zone?: string;
    garden_plants: GardenPlant[];
};

type GardenType = {
    id: number;
    name: string;
};

const GardenView = () => {
    const auth = useContext(AuthContext);
    const token = auth?.isAuthenticated
        ? localStorage.getItem("token") ?? undefined
        : undefined;

    // State management
    const [gardens, setGardens] = useState<Garden[]>([]);
    const [plants, setPlants] = useState<Plant[]>([]);
    const [gardenTypes, setGardenTypes] = useState<GardenType[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Form state for new gardens
    const [showNewGardenForm, setShowNewGardenForm] = useState(false);
    const [newGarden, setNewGarden] = useState({
        garden_name: "",
        garden_type: "",
        garden_size: "",
        water_source: "",
        soil_type: "",
    });

    // Form state for adding plants to gardens
    const [showAddPlantForm, setShowAddPlantForm] = useState(false);
    const [selectedGardenId, setSelectedGardenId] = useState<number | null>(
        null
    );
    const [newPlant, setNewPlant] = useState({
        plant_id: 0,
        expected_harvest_date: "",
        growth_stage: "Seedling",
    });

    // Fetch gardens, plants and garden types on component mount
    useEffect(() => {
        const fetchData = async () => {
            if (!token) {
                setLoading(false);
                return;
            }

            try {
                // Fetch gardens
                const gardensResponse = await api.get("/user_gardens", token);
                console.log("Gardens response:", gardensResponse);

                // Add empty plant arrays if none exist
                const gardensWithPlants = Array.isArray(gardensResponse)
                    ? gardensResponse.map((garden) => ({
                          ...garden,
                          garden_plants: garden.garden_plants || [],
                      }))
                    : [];

                setGardens(gardensWithPlants);

                // Fetch plants
                const plantsResponse = await api.get("/plants/get_plants");
                console.log("Plants response:", plantsResponse);
                setPlants(plantsResponse.plants || []);

                // Fetch garden types
                const gardenTypesResponse = await api.get("/garden_types");
                console.log("Garden types response:", gardenTypesResponse);
                setGardenTypes(gardenTypesResponse || []);
            } catch (err: any) {
                console.error("Error fetching garden data:", err);
                setError(err.message || "Failed to fetch garden data");
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [token]);

    // Toggle new garden form
    const toggleNewGardenForm = () => {
        setShowNewGardenForm(!showNewGardenForm);
        // Reset form when toggling
        setNewGarden({
            garden_name: "",
            garden_type: "",
            garden_size: "",
            water_source: "",
            soil_type: "",
        });
    };

    // Toggle add plant form
    const toggleAddPlantForm = (gardenId: number | null) => {
        setSelectedGardenId(gardenId);
        setShowAddPlantForm(gardenId !== null);
        // Reset form when toggling
        setNewPlant({
            plant_id: plants.length > 0 ? plants[0].id : 0,
            expected_harvest_date: "",
            growth_stage: "Seedling",
        });
    };

    // Handle input changes for new garden form
    const handleGardenInputChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
    ) => {
        const { name, value } = e.target;
        setNewGarden((prev) => ({ ...prev, [name]: value }));
    };

    // Handle input changes for add plant form
    const handlePlantInputChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
    ) => {
        const { name, value } = e.target;
        setNewPlant((prev) => ({ ...prev, [name]: value }));
    };

    // Create new garden
    const handleCreateGarden = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!token) return;

        try {
            setLoading(true);
            const response = await api.post("/user_gardens", newGarden, token);

            console.log("Garden created:", response);

            // Add the new garden to state
            if (response.garden_id) {
                const createdGarden = {
                    id: response.garden_id,
                    ...newGarden,
                    garden_plants: [],
                } as Garden;

                setGardens((prevGardens) => [...prevGardens, createdGarden]);
                toggleNewGardenForm(); // Close the form
            }
        } catch (err: any) {
            console.error("Error creating garden:", err);
            setError(err.message || "Failed to create garden");
        } finally {
            setLoading(false);
        }
    };

    // Add plant to garden
    const handleAddPlant = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!token || selectedGardenId === null) return;

        try {
            setLoading(true);
            const payload = {
                garden_id: selectedGardenId,
                ...newPlant,
            };

            const response = await api.post(
                "/user_garden_plants",
                payload,
                token
            );

            console.log("Plant added:", response);

            // Add the plant to the garden in state
            if (response.garden_plant_id) {
                // Find the plant to get its name
                const plant = plants.find((p) => p.id === newPlant.plant_id);

                const addedPlant: GardenPlant = {
                    id: response.garden_plant_id,
                    plant_id: newPlant.plant_id,
                    plant_name: plant?.name || "Unknown Plant",
                    growth_stage: newPlant.growth_stage,
                    expected_harvest_date: newPlant.expected_harvest_date,
                };

                setGardens((prevGardens) =>
                    prevGardens.map((garden) => {
                        if (garden.id === selectedGardenId) {
                            return {
                                ...garden,
                                garden_plants: [
                                    ...garden.garden_plants,
                                    addedPlant,
                                ],
                            };
                        }
                        return garden;
                    })
                );

                toggleAddPlantForm(null); // Close the form
            }
        } catch (err: any) {
            console.error("Error adding plant:", err);
            setError(err.message || "Failed to add plant");
        } finally {
            setLoading(false);
        }
    };

    // Delete a garden
    const handleDeleteGarden = async (gardenId: number) => {
        if (!token) return;

        if (!window.confirm("Are you sure you want to delete this garden?")) {
            return;
        }

        try {
            setLoading(true);
            await api.deleteRequest(`/user_gardens/${gardenId}`, token);

            // Remove the garden from state
            setGardens((prevGardens) =>
                prevGardens.filter((garden) => garden.id !== gardenId)
            );
        } catch (err: any) {
            console.error("Error deleting garden:", err);
            setError(err.message || "Failed to delete garden");
        } finally {
            setLoading(false);
        }
    };

    // Remove a plant from a garden
    const handleRemovePlant = async (
        gardenPlantId: number,
        gardenId: number
    ) => {
        if (!token) return;

        if (!window.confirm("Are you sure you want to remove this plant?")) {
            return;
        }

        try {
            setLoading(true);
            await api.deleteRequest(
                `/user_garden_plants/${gardenPlantId}`,
                token
            );

            // Remove the plant from the garden in state
            setGardens((prevGardens) =>
                prevGardens.map((garden) => {
                    if (garden.id === gardenId) {
                        return {
                            ...garden,
                            garden_plants: garden.garden_plants.filter(
                                (plant) => plant.id !== gardenPlantId
                            ),
                        };
                    }
                    return garden;
                })
            );
        } catch (err: any) {
            console.error("Error removing plant:", err);
            setError(err.message || "Failed to remove plant");
        } finally {
            setLoading(false);
        }
    };

    // Clear error message
    const clearError = () => {
        setError(null);
    };

    if (loading && gardens.length === 0) {
        return (
            <div className={styles.container}>
                <p>Loading your gardens...</p>
            </div>
        );
    }

    return (
        <div className={styles.container}>
            <h1 className={styles.pageTitle}>My Gardens</h1>

            {/* Error message display */}
            {error && (
                <div className={styles.errorMessage}>
                    <p>{error}</p>
                    <button onClick={clearError} className={styles.closeButton}>
                        ×
                    </button>
                </div>
            )}

            {/* Button to toggle new garden form */}
            <button
                onClick={toggleNewGardenForm}
                className={styles.primaryButton}
            >
                {showNewGardenForm ? "Cancel" : "Create New Garden"}
            </button>

            {/* New Garden Form */}
            {showNewGardenForm && (
                <div className={styles.formContainer}>
                    <h2>Create New Garden</h2>
                    <form onSubmit={handleCreateGarden} className={styles.form}>
                        <div className={styles.formGroup}>
                            <label htmlFor="garden_name">Garden Name:</label>
                            <input
                                type="text"
                                id="garden_name"
                                name="garden_name"
                                value={newGarden.garden_name}
                                onChange={handleGardenInputChange}
                                required
                            />
                        </div>

                        <div className={styles.formGroup}>
                            <label htmlFor="garden_type">Garden Type:</label>
                            <select
                                id="garden_type"
                                name="garden_type"
                                value={newGarden.garden_type}
                                onChange={handleGardenInputChange}
                                required
                            >
                                <option value="">Select Garden Type</option>
                                {gardenTypes.map((type) => (
                                    <option key={type.id} value={type.name}>
                                        {type.name}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div className={styles.formGroup}>
                            <label htmlFor="garden_size">Garden Size:</label>
                            <input
                                type="text"
                                id="garden_size"
                                name="garden_size"
                                value={newGarden.garden_size}
                                onChange={handleGardenInputChange}
                                placeholder="e.g., 10x10 ft"
                            />
                        </div>

                        <div className={styles.formGroup}>
                            <label htmlFor="water_source">Water Source:</label>
                            <input
                                type="text"
                                id="water_source"
                                name="water_source"
                                value={newGarden.water_source}
                                onChange={handleGardenInputChange}
                                placeholder="e.g., Drip Irrigation, Rain Barrel"
                            />
                        </div>

                        <div className={styles.formGroup}>
                            <label htmlFor="soil_type">Soil Type:</label>
                            <input
                                type="text"
                                id="soil_type"
                                name="soil_type"
                                value={newGarden.soil_type}
                                onChange={handleGardenInputChange}
                                placeholder="e.g., Clay, Sandy, Loam"
                            />
                        </div>

                        <button type="submit" className={styles.submitButton}>
                            Create Garden
                        </button>
                    </form>
                </div>
            )}

            {/* Display Gardens */}
            <div className={styles.gardensGrid}>
                {gardens.length === 0 ? (
                    <p className={styles.noGardensMessage}>
                        You haven't created any gardens yet. Create your first
                        garden to get started!
                    </p>
                ) : (
                    gardens.map((garden) => (
                        <div key={garden.id} className={styles.gardenCard}>
                            <div className={styles.gardenHeader}>
                                <h2>{garden.garden_name}</h2>
                                <div className={styles.gardenActions}>
                                    <button
                                        onClick={() =>
                                            toggleAddPlantForm(garden.id)
                                        }
                                        className={styles.addButton}
                                    >
                                        Add Plant
                                    </button>
                                    <button
                                        onClick={() =>
                                            handleDeleteGarden(garden.id)
                                        }
                                        className={styles.deleteButton}
                                    >
                                        Delete Garden
                                    </button>
                                </div>
                            </div>

                            <div className={styles.gardenDetails}>
                                <p>
                                    <strong>Type:</strong> {garden.garden_type}
                                </p>
                                {garden.garden_size && (
                                    <p>
                                        <strong>Size:</strong>{" "}
                                        {garden.garden_size}
                                    </p>
                                )}
                                {garden.water_source && (
                                    <p>
                                        <strong>Water Source:</strong>{" "}
                                        {garden.water_source}
                                    </p>
                                )}
                                {garden.soil_type && (
                                    <p>
                                        <strong>Soil Type:</strong>{" "}
                                        {garden.soil_type}
                                    </p>
                                )}
                                {garden.plant_hardiness_zone && (
                                    <p>
                                        <strong>Hardiness Zone:</strong>{" "}
                                        {garden.plant_hardiness_zone}
                                    </p>
                                )}
                            </div>

                            <div className={styles.plantsSection}>
                                <h3>Plants</h3>
                                {garden.garden_plants &&
                                garden.garden_plants.length > 0 ? (
                                    <div className={styles.plantsGrid}>
                                        {garden.garden_plants.map((plant) => (
                                            <div
                                                key={plant.id}
                                                className={styles.plantCard}
                                            >
                                                <div
                                                    className={
                                                        styles.plantHeader
                                                    }
                                                >
                                                    <h4>{plant.plant_name}</h4>
                                                    <button
                                                        onClick={() =>
                                                            handleRemovePlant(
                                                                plant.id,
                                                                garden.id
                                                            )
                                                        }
                                                        className={
                                                            styles.removePlantButton
                                                        }
                                                    >
                                                        ×
                                                    </button>
                                                </div>
                                                <p>
                                                    <strong>
                                                        Growth Stage:
                                                    </strong>{" "}
                                                    {plant.growth_stage}
                                                </p>
                                                {plant.expected_harvest_date && (
                                                    <p>
                                                        <strong>
                                                            Expected Harvest:
                                                        </strong>{" "}
                                                        {new Date(
                                                            plant.expected_harvest_date
                                                        ).toLocaleDateString()}
                                                    </p>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <p className={styles.noPlantMessage}>
                                        No plants added yet.
                                    </p>
                                )}
                            </div>
                        </div>
                    ))
                )}
            </div>

            {/* Add Plant Form */}
            {showAddPlantForm && selectedGardenId && (
                <div className={styles.modalBackdrop}>
                    <div className={styles.modalContent}>
                        <div className={styles.modalHeader}>
                            <h2>Add Plant to Garden</h2>
                            <button
                                onClick={() => toggleAddPlantForm(null)}
                                className={styles.closeButton}
                            >
                                ×
                            </button>
                        </div>

                        <form onSubmit={handleAddPlant} className={styles.form}>
                            <div className={styles.formGroup}>
                                <label htmlFor="plant_id">Plant:</label>
                                <select
                                    id="plant_id"
                                    name="plant_id"
                                    value={newPlant.plant_id}
                                    onChange={handlePlantInputChange}
                                    required
                                >
                                    <option value="">Select Plant</option>
                                    {plants.map((plant) => (
                                        <option key={plant.id} value={plant.id}>
                                            {plant.name}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div className={styles.formGroup}>
                                <label htmlFor="growth_stage">
                                    Growth Stage:
                                </label>
                                <select
                                    id="growth_stage"
                                    name="growth_stage"
                                    value={newPlant.growth_stage}
                                    onChange={handlePlantInputChange}
                                    required
                                >
                                    <option value="Seedling">Seedling</option>
                                    <option value="Vegetative">
                                        Vegetative
                                    </option>
                                    <option value="Flowering">Flowering</option>
                                    <option value="Fruiting">Fruiting</option>
                                </select>
                            </div>

                            <div className={styles.formGroup}>
                                <label htmlFor="expected_harvest_date">
                                    Expected Harvest Date:
                                </label>
                                <input
                                    type="date"
                                    id="expected_harvest_date"
                                    name="expected_harvest_date"
                                    value={newPlant.expected_harvest_date}
                                    onChange={handlePlantInputChange}
                                />
                            </div>

                            <button
                                type="submit"
                                className={styles.submitButton}
                            >
                                Add Plant
                            </button>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default GardenView;
