import { useState, useEffect, useContext } from "react";
import { useParams, Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import api from "../services/api";
import styles from "../styles/GardenMap.module.css";

type Plant = {
    id: number;
    name: string;
    description?: string;
    sunlight?: string;
    waterNeeds?: string;
    spaceRequired?: string;
};

type Placement = {
    id: number;
    plant_id: number;
    plant_name: string;
    growth_stage: string;
    row: number | null;
    col: number | null;
    image_url?: string;
    expected_harvest_date?: string;
};

type PlantInfo = {
    plant: {
        id: number;
        name: string;
        scientific_name?: string;
        description?: string;
        image_url?: string;
        sunlight?: string;
        water_needs?: string;
        growing_season?: string;
        space_required?: string;
        sowing_method?: string;
        spread?: number;
        row_spacing?: number;
        height?: number;
        hardiness_min?: string;
        hardiness_max?: string;
    };
    placement: {
        id: number;
        row: number;
        col: number;
        growth_stage: string;
        planted_at?: string;
        expected_harvest_date?: string;
    };
    companions: {
        good_companions: string[];
        bad_companions: string[];
        tips: string[];
    };
    spacing: string[];
};

// Assign a consistent color to each plant based on its id
const PLANT_COLORS = [
    "#4caf50", "#8bc34a", "#cddc39", "#ff9800", "#f44336",
    "#e91e63", "#9c27b0", "#673ab7", "#3f51b5", "#2196f3",
    "#00bcd4", "#009688", "#795548", "#607d8b", "#ff5722",
];

function getPlantColor(plantId: number): string {
    return PLANT_COLORS[plantId % PLANT_COLORS.length];
}

const GardenMap = () => {
    const { gardenId } = useParams<{ gardenId: string }>();
    const auth = useContext(AuthContext);
    const { showToast } = useToast();
    const token = auth?.isAuthenticated
        ? localStorage.getItem("token") ?? undefined
        : undefined;

    const [gardenName, setGardenName] = useState("");
    const [gridRows, setGridRows] = useState(8);
    const [gridCols, setGridCols] = useState(10);
    const [placements, setPlacements] = useState<Placement[]>([]);
    const [plants, setPlants] = useState<Plant[]>([]);
    const [selectedPlantId, setSelectedPlantId] = useState<number | null>(null);
    const [plantInfo, setPlantInfo] = useState<PlantInfo | null>(null);
    const [showInfoPanel, setShowInfoPanel] = useState(false);
    const [showResizeForm, setShowResizeForm] = useState(false);
    const [newRows, setNewRows] = useState(8);
    const [newCols, setNewCols] = useState(10);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [mode, setMode] = useState<"place" | "view">("place");
    const [paletteSearch, setPaletteSearch] = useState("");

    const id = Number(gardenId);

    // Load map data and plant list
    useEffect(() => {
        const fetchData = async () => {
            if (!token || !gardenId) {
                setLoading(false);
                return;
            }

            try {
                const [mapData, plantsData] = await Promise.all([
                    api.getGardenMap(id, token),
                    api.getPlants(),
                ]);

                setGardenName(mapData.garden_name);
                setGridRows(mapData.grid_rows);
                setGridCols(mapData.grid_cols);
                setNewRows(mapData.grid_rows);
                setNewCols(mapData.grid_cols);
                setPlacements(mapData.placements || []);
                setPlants(plantsData.plants || []);
            } catch (err: any) {
                console.error("Error loading garden map:", err);
                setError("Failed to load garden map.");
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [token, gardenId]);

    // Build a lookup grid: [row][col] -> placement
    const grid: (Placement | null)[][] = [];
    for (let r = 0; r < gridRows; r++) {
        grid[r] = [];
        for (let c = 0; c < gridCols; c++) {
            grid[r][c] = null;
        }
    }
    for (const p of placements) {
        if (p.row !== null && p.col !== null && p.row < gridRows && p.col < gridCols) {
            grid[p.row][p.col] = p;
        }
    }

    const handleCellClick = async (row: number, col: number) => {
        if (!token) return;

        const existing = grid[row][col];

        if (existing) {
            // Click on existing plant -> show info
            try {
                const info = await api.getPlantMapInfo(id, existing.id, token);
                setPlantInfo(info);
                setShowInfoPanel(true);
            } catch (err: any) {
                setError("Failed to load plant info.");
            }
            return;
        }

        // Place a new plant if one is selected
        if (mode === "place" && selectedPlantId) {
            try {
                const result = await api.placePlantOnMap(
                    id,
                    { plant_id: selectedPlantId, row, col },
                    token
                );

                const newPlacement: Placement = {
                    id: result.garden_plant_id,
                    plant_id: selectedPlantId,
                    plant_name: result.plant_name,
                    growth_stage: "Seedling",
                    row,
                    col,
                    image_url: result.image_url,
                };
                setPlacements((prev) => [...prev, newPlacement]);
                showToast(`${result.plant_name} placed on map!`);
            } catch (err: any) {
                setError(err.message || "Failed to place plant.");
            }
        }
    };

    const handleRemovePlant = async (gardenPlantId: number) => {
        if (!token) return;

        try {
            await api.removePlantFromMap(id, gardenPlantId, token);
            setPlacements((prev) => prev.filter((p) => p.id !== gardenPlantId));
            setShowInfoPanel(false);
            setPlantInfo(null);
            showToast("Plant removed from map.");
        } catch (err: any) {
            setError(err.message || "Failed to remove plant.");
        }
    };

    const handleResize = async () => {
        if (!token) return;

        try {
            await api.resizeGardenGrid(id, { grid_rows: newRows, grid_cols: newCols }, token);
            setGridRows(newRows);
            setGridCols(newCols);
            // Remove placements outside new bounds
            setPlacements((prev) =>
                prev.map((p) => {
                    if (p.row !== null && p.col !== null && (p.row >= newRows || p.col >= newCols)) {
                        return { ...p, row: null, col: null };
                    }
                    return p;
                })
            );
            setShowResizeForm(false);
        } catch (err: any) {
            setError(err.message || "Failed to resize grid.");
        }
    };

    if (loading) {
        return (
            <div className={styles.container}>
                <div className="skeleton" style={{ height: "1rem", width: "140px", marginBottom: "var(--space-sm)" }} />
                <div className="skeleton" style={{ height: "2rem", width: "300px", marginBottom: "var(--space-xl)" }} />
                <div style={{ display: "flex", gap: "var(--space-xl)" }}>
                    <div className="skeleton" style={{ width: "220px", height: "400px", borderRadius: "var(--radius-lg)", flexShrink: 0 }} />
                    <div className="skeleton" style={{ flex: 1, height: "400px", borderRadius: "var(--radius-md)" }} />
                </div>
            </div>
        );
    }

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <div className={styles.headerLeft}>
                    <Link to="/gardens" className={styles.backLink}>
                        Back to Gardens
                    </Link>
                    <h1 className={styles.pageTitle}>{gardenName} - Garden Map</h1>
                </div>
                <div className={styles.headerActions}>
                    <button
                        onClick={() => setMode(mode === "place" ? "view" : "place")}
                        className={`${styles.modeButton} ${mode === "place" ? styles.modeActive : ""}`}
                    >
                        {mode === "place" ? "Placing Mode" : "View Mode"}
                    </button>
                    <button
                        onClick={() => setShowResizeForm(!showResizeForm)}
                        className={styles.resizeButton}
                    >
                        Resize Grid
                    </button>
                </div>
            </div>

            {error && (
                <div className={styles.errorMessage}>
                    <p>{error}</p>
                    <button onClick={() => setError(null)} className={styles.closeButton}>
                        &times;
                    </button>
                </div>
            )}

            {/* Resize Form */}
            {showResizeForm && (
                <div className={styles.resizeForm}>
                    <label>
                        Rows:
                        <input
                            type="number"
                            value={newRows}
                            onChange={(e) => setNewRows(Math.max(1, Math.min(50, Number(e.target.value))))}
                            min="1"
                            max="50"
                        />
                    </label>
                    <label>
                        Columns:
                        <input
                            type="number"
                            value={newCols}
                            onChange={(e) => setNewCols(Math.max(1, Math.min(50, Number(e.target.value))))}
                            min="1"
                            max="50"
                        />
                    </label>
                    <button onClick={handleResize} className={styles.applyButton}>
                        Apply
                    </button>
                    <button onClick={() => setShowResizeForm(false)} className={styles.cancelButton}>
                        Cancel
                    </button>
                </div>
            )}

            <div className={styles.mapLayout}>
                {/* Plant Palette Sidebar */}
                <div className={styles.palette}>
                    <h2 className={styles.paletteTitle}>Plants</h2>
                    {mode === "place" && (
                        <p className={styles.paletteHint}>
                            Select a plant, then click an empty cell to place it.
                        </p>
                    )}
                    <input
                        type="text"
                        className={styles.paletteSearch}
                        placeholder="Search plants..."
                        value={paletteSearch}
                        onChange={(e) => setPaletteSearch(e.target.value)}
                    />
                    <div className={styles.plantList}>
                        {plants.filter((plant) =>
                            plant.name.toLowerCase().includes(paletteSearch.toLowerCase())
                        ).map((plant) => (
                            <button
                                key={plant.id}
                                className={`${styles.plantOption} ${
                                    selectedPlantId === plant.id
                                        ? styles.plantSelected
                                        : ""
                                }`}
                                onClick={() => setSelectedPlantId(plant.id)}
                                style={{
                                    borderLeftColor: getPlantColor(plant.id),
                                }}
                            >
                                <span className={styles.plantName}>
                                    {plant.name}
                                </span>
                                {plant.sunlight && (
                                    <span className={styles.plantMeta}>
                                        {plant.sunlight}
                                    </span>
                                )}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Grid */}
                <div className={styles.gridWrapper}>
                    <div
                        className={styles.grid}
                        style={{
                            gridTemplateColumns: `repeat(${gridCols}, 1fr)`,
                            gridTemplateRows: `repeat(${gridRows}, 1fr)`,
                        }}
                    >
                        {grid.map((row, rowIdx) =>
                            row.map((cell, colIdx) => (
                                <div
                                    key={`${rowIdx}-${colIdx}`}
                                    className={`${styles.cell} ${
                                        cell ? styles.cellOccupied : styles.cellEmpty
                                    } ${
                                        mode === "place" && selectedPlantId && !cell
                                            ? styles.cellPlaceable
                                            : ""
                                    }`}
                                    onClick={() => handleCellClick(rowIdx, colIdx)}
                                    title={
                                        cell
                                            ? `${cell.plant_name} (${cell.growth_stage})`
                                            : `Row ${rowIdx + 1}, Col ${colIdx + 1}`
                                    }
                                    style={
                                        cell
                                            ? {
                                                  backgroundColor: getPlantColor(cell.plant_id),
                                              }
                                            : undefined
                                    }
                                >
                                    {cell && (
                                        <div className={styles.cellContent}>
                                            <span className={styles.cellLabel}>
                                                {cell.plant_name.length > 8
                                                    ? cell.plant_name.slice(0, 7) + "..."
                                                    : cell.plant_name}
                                            </span>
                                        </div>
                                    )}
                                </div>
                            ))
                        )}
                    </div>
                    <div className={styles.gridLegend}>
                        <span>{gridRows} rows &times; {gridCols} cols</span>
                        <span>{placements.filter((p) => p.row !== null).length} plants placed</span>
                    </div>
                </div>
            </div>

            {/* Plant Info Panel */}
            {showInfoPanel && plantInfo && (
                <div className={styles.infoPanelBackdrop} onClick={() => setShowInfoPanel(false)}>
                    <div className={styles.infoPanel} onClick={(e) => e.stopPropagation()}>
                        <div className={styles.infoPanelHeader}>
                            <h2>{plantInfo.plant.name}</h2>
                            <button
                                onClick={() => setShowInfoPanel(false)}
                                className={styles.closeButton}
                            >
                                &times;
                            </button>
                        </div>

                        {plantInfo.plant.scientific_name && (
                            <p className={styles.scientificName}>
                                <em>{plantInfo.plant.scientific_name}</em>
                            </p>
                        )}

                        {plantInfo.plant.image_url && (
                            <img
                                src={plantInfo.plant.image_url}
                                alt={plantInfo.plant.name}
                                className={styles.plantImage}
                            />
                        )}

                        {plantInfo.plant.description && (
                            <p className={styles.description}>
                                {plantInfo.plant.description}
                            </p>
                        )}

                        {/* Growing Details */}
                        <div className={styles.infoSection}>
                            <h3>Growing Details</h3>
                            <div className={styles.detailsGrid}>
                                {plantInfo.plant.sunlight && (
                                    <div className={styles.detailItem}>
                                        <span className={styles.detailLabel}>Sunlight</span>
                                        <span className={styles.detailValue}>{plantInfo.plant.sunlight}</span>
                                    </div>
                                )}
                                {plantInfo.plant.water_needs && (
                                    <div className={styles.detailItem}>
                                        <span className={styles.detailLabel}>Water</span>
                                        <span className={styles.detailValue}>{plantInfo.plant.water_needs}</span>
                                    </div>
                                )}
                                {plantInfo.plant.growing_season && (
                                    <div className={styles.detailItem}>
                                        <span className={styles.detailLabel}>Season</span>
                                        <span className={styles.detailValue}>{plantInfo.plant.growing_season}</span>
                                    </div>
                                )}
                                {plantInfo.plant.space_required && (
                                    <div className={styles.detailItem}>
                                        <span className={styles.detailLabel}>Space</span>
                                        <span className={styles.detailValue}>{plantInfo.plant.space_required}</span>
                                    </div>
                                )}
                                {plantInfo.plant.sowing_method && (
                                    <div className={styles.detailItem}>
                                        <span className={styles.detailLabel}>Sowing</span>
                                        <span className={styles.detailValue}>{plantInfo.plant.sowing_method}</span>
                                    </div>
                                )}
                                {plantInfo.plant.hardiness_min && plantInfo.plant.hardiness_max && (
                                    <div className={styles.detailItem}>
                                        <span className={styles.detailLabel}>Hardiness</span>
                                        <span className={styles.detailValue}>
                                            {plantInfo.plant.hardiness_min} - {plantInfo.plant.hardiness_max}
                                        </span>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Spacing Info */}
                        {plantInfo.spacing.length > 0 && (
                            <div className={styles.infoSection}>
                                <h3>Spacing</h3>
                                <ul className={styles.spacingList}>
                                    {plantInfo.spacing.map((tip, i) => (
                                        <li key={i}>{tip}</li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        {/* Placement Info */}
                        <div className={styles.infoSection}>
                            <h3>Placement</h3>
                            <p>
                                Position: Row {plantInfo.placement.row + 1}, Column{" "}
                                {plantInfo.placement.col + 1}
                            </p>
                            <p>Growth Stage: {plantInfo.placement.growth_stage}</p>
                            {plantInfo.placement.planted_at && (
                                <p>
                                    Planted:{" "}
                                    {new Date(plantInfo.placement.planted_at).toLocaleDateString()}
                                </p>
                            )}
                        </div>

                        {/* Companion Planting */}
                        <div className={styles.infoSection}>
                            <h3>Companion Planting</h3>
                            {plantInfo.companions.good_companions.length > 0 && (
                                <div className={styles.companionGroup}>
                                    <span className={styles.companionLabel}>
                                        Good neighbors in your garden:
                                    </span>
                                    <div className={styles.companionTags}>
                                        {plantInfo.companions.good_companions.map((name) => (
                                            <span key={name} className={styles.tagGood}>
                                                {name}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}
                            {plantInfo.companions.bad_companions.length > 0 && (
                                <div className={styles.companionGroup}>
                                    <span className={styles.companionLabel}>
                                        Bad neighbors in your garden:
                                    </span>
                                    <div className={styles.companionTags}>
                                        {plantInfo.companions.bad_companions.map((name) => (
                                            <span key={name} className={styles.tagBad}>
                                                {name}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}
                            {plantInfo.companions.good_companions.length === 0 &&
                                plantInfo.companions.bad_companions.length === 0 && (
                                    <p className={styles.noCompanions}>
                                        No companion data for neighboring plants.
                                    </p>
                                )}
                            {plantInfo.companions.tips.map((tip, i) => (
                                <p key={i} className={styles.companionTip}>
                                    {tip}
                                </p>
                            ))}
                        </div>

                        {/* Remove Button */}
                        <button
                            onClick={() => handleRemovePlant(plantInfo.placement.id)}
                            className={styles.removeButton}
                        >
                            Remove from Map
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default GardenMap;
