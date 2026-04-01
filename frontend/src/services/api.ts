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

// Helper function to make PUT requests
async function put(endpoint: string, body: object, token?: string) {
    const headers: HeadersInit = { "Content-Type": "application/json" };
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api${endpoint}`, {
            method: "PUT",
            headers,
            body: JSON.stringify(body),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `Failed to update ${endpoint}`);
        }
        return response.json();
    } catch (error) {
        console.error(`API PUT Error (${endpoint}):`, error);
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
async function getPlants(filters?: Record<string, string>) {
    const params = new URLSearchParams(filters || {}).toString();
    const query = params ? `?${params}` : "";
    return get(`/plants/get_plants${query}`);
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

async function updateGarden(gardenId: number, gardenData: object, token: string) {
    return put(`/user_gardens/${gardenId}`, gardenData, token);
}

// Weather API call
async function getWeather(zip: string) {
    return get(`/weather/get_weather?zip=${zip}`);
}

// Frost dates API calls
async function getFrostDates(zip: string) {
    return get(`/frost_dates?zip=${zip}`);
}

async function getFrostDatesByZone(zone: string) {
    return get(`/frost_dates?zone=${zone}`);
}

// User API calls
async function getUser(token: string) {
    return get("/users/get_user", token);
}

async function getProfile(token: string) {
    return get("/users/profile", token);
}

// Garden map API calls
async function getGardenMap(gardenId: number, token: string) {
    return get(`/user_gardens/${gardenId}/map`, token);
}

async function resizeGardenGrid(gardenId: number, gridData: { grid_rows: number; grid_cols: number }, token: string) {
    return put(`/user_gardens/${gardenId}/map/resize`, gridData, token);
}

async function placePlantOnMap(gardenId: number, plantData: { plant_id: number; row: number; col: number; growth_stage?: string }, token: string) {
    return post(`/user_gardens/${gardenId}/map/place`, plantData, token);
}

async function removePlantFromMap(gardenId: number, gardenPlantId: number, token: string) {
    return deleteRequest(`/user_gardens/${gardenId}/map/${gardenPlantId}`, token);
}

async function getPlantMapInfo(gardenId: number, gardenPlantId: number, token: string) {
    return get(`/user_gardens/${gardenId}/map/${gardenPlantId}/info`, token);
}

async function getPlantDetails(plantId: number) {
    return get(`/plants/${plantId}`);
}

// Journal API calls
async function getJournalEntries(gardenId: number, token: string) {
    return get(`/journal/${gardenId}`, token);
}

async function getRecentJournalEntries(gardenId: number, token: string) {
    return get(`/journal/${gardenId}/recent`, token);
}

async function createJournalEntry(data: object, token: string) {
    return post("/journal", data, token);
}

async function deleteJournalEntry(entryId: number, token: string) {
    return deleteRequest(`/journal/${entryId}`, token);
}

// Planting calendar API calls
async function getPlantingCalendar(zone: string) {
    return get(`/planting_calendar?zone=${zone}`);
}

// Tasks API calls
async function getTasks(token: string) {
    return get("/tasks", token);
}

// Weather alerts API calls
async function getWeatherAlerts(token: string) {
    return get("/weather_alerts", token);
}

// Recommendations API calls
async function getRecommendations(token: string) {
    return get("/recommendations", token);
}

async function getSeasonalRecommendations(token: string) {
    return get("/recommendations/seasonal", token);
}

// Harvest API calls
async function logHarvest(data: object, token: string) {
    return post("/harvests", data, token);
}

async function getHarvests(gardenId: number, token: string) {
    return get(`/harvests/${gardenId}`, token);
}

async function getHarvestSummary(token: string) {
    return get("/harvests/summary", token);
}

async function deleteHarvest(harvestId: number, token: string) {
    return deleteRequest(`/harvests/${harvestId}`, token);
}

// Soil API calls
async function getSoilRecommendations(token: string) {
    return get("/soil/recommendations", token);
}

async function getPhGuide() {
    return get("/soil/ph-guide");
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
    updateGarden,
    getWeather,
    getFrostDates,
    getFrostDatesByZone,
    getUser,
    getProfile,
    getGardenMap,
    resizeGardenGrid,
    placePlantOnMap,
    removePlantFromMap,
    getPlantMapInfo,
    getPlantDetails,
    getJournalEntries,
    getRecentJournalEntries,
    createJournalEntry,
    deleteJournalEntry,
    getPlantingCalendar,
    getTasks,
    getWeatherAlerts,
    getRecommendations,
    getSeasonalRecommendations,
    logHarvest,
    getHarvests,
    getHarvestSummary,
    deleteHarvest,
    getSoilRecommendations,
    getPhGuide,
    get,
    post,
    put,
    deleteRequest,
};