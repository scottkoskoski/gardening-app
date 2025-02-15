const API_BASE_URL = "http://127.0.0.1:5000/api";

export async function getPlants() {
    const response = await fetch(`${API_BASE_URL}/plants/get_plants`);
    if (!response.ok) {
        throw new Error("Failed to fetch plants");
    }
    return response.json();
}