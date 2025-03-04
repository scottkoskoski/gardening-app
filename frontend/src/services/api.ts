const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000"; // Use env variable or fallback

// Helper function to make GET requests
async function get(endpoint: string, token?: string) {
    const headers: HeadersInit = {};
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api${endpoint}`, { headers });
        if (!response.ok) {
            throw new Error(`Failed to fetch ${endpoint}`);
        }
        return response.json();
    } catch (error) {
        console.error(`API GET Error (${endpoint}):`, error);
        throw error;
    }
}


// Helper function to make POST requests
async function post(endpoint: string, body: object, token?: string) {
    const headers: HeadersInit = { "Content-Type": "application/json" };
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api${endpoint}`, {
            method: "POST",
            headers,
            body: JSON.stringify(body),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `Failed to post to ${endpoint}`);
        }
        return response.json();
    } catch (error) {
        console.error(`API POST Error (${endpoint}):`, error);
        throw error;
    }
}

// Helper function to make DELETE requests
async function deleteRequest(endpoint: string, token?: string) {
    const headers: HeadersInit = {};
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api${endpoint}`, {
            method: "DELETE",
            headers,
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `Failed to delete ${endpoint}`);
        }
        return response.json()
    } catch (error) {
        console.error(`API DELETE Error (${endpoint}):`, error);
        throw error;
    }
}


// Plant-related API calls
async function getPlants() {
    return get("/plants/get_plants");
}

// Fetch plant hardiness zone
async function getHardinessZone(zip: string) {
    return get(`/hardiness/get_hardiness_zone?zip=${zip}`);
}

// Garden type API calls
async function getGardenTypes() {
    return get("/garden_types");
}

// User gardens API calls
async function getUserGardens(token: string) {
    return get("/user_gardens", token);
}

async function createGarden(gardenData: Object, token: string) {
    return post("/user_gardens", gardenData, token);
}

async function addPlantToGarden(plantData: Object, token: string) {
    return post("/user_garden_plants", plantData, token);
}

async function deleteGarden(gardenId: number, token: string) {
    return deleteRequest(`/user_gardens/${gardenId}`, token);
}

async function removePlantFromGarden(plantId: number, token: string) {
    return deleteRequest(`/user_garden_plants/${plantId}`, token);
}


export default {
    getPlants,
    getHardinessZone,
    getGardenTypes,
    getUserGardens,
    createGarden,
    addPlantToGarden,
    deleteGarden,
    removePlantFromGarden,
    get,
    post,
    deleteRequest,
};