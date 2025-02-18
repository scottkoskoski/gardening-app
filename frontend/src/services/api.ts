const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000"; // Use env variable or fallback

// Helper function to make GET requests
async function get(endpoint: string, token?: string) {
    const headers: HeadersInit = {};
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/api${endpoint}`, { headers });
    if (!response.ok) {
        throw new Error(`Failed to fetch ${endpoint}`);
    }
    return response.json();
}

// Helper function to make POST requests
async function post(endpoint: string, body: object, token?: string) {
    const headers: HeadersInit = { "Content-Type": "application/json" };
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/api${endpoint}`, {
        method: "POST",
        headers,
        body: JSON.stringify(body),
    });

    if (!response.ok) throw new Error(`Failed to post ${endpoint}`);
    return response.json();
}

// Plant-related API calls
async function getPlants() {
    return get("/plants/get_plants");
}

// Fetch plant hardiness zone
async function getHardinessZone(zip: string) {
    return get(`/hardiness/get_hardiness_zone?zip=${zip}`);
}

export default {
    getPlants,
    getHardinessZone,
    get,
    post,
};