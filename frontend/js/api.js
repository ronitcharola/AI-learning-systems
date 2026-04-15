const API_URL = 'https://ai-learning-systems-2.onrender.com/api';

class ApiService {
    constructor() {
        this.token = localStorage.getItem('token');
        this.user = JSON.parse(localStorage.getItem('user')) || null;
    }

    setToken(token, user) {
        this.token = token;
        this.user = user;
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(user));
    }

    logout() {
        this.token = null;
        this.user = null;
        localStorage.removeItem('token');
        localStorage.removeItem('user');
    }

    async request(endpoint, options = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const config = {
            ...options,
            headers
        };

        try {
            const response = await fetch(`${API_URL}${endpoint}`, config);
            const data = await response.json();
            
            if (!response.ok) {
                // If token expired, could auto-logout here
                if (response.status === 401) {
                    this.logout();
                }
                throw new Error(data.message || 'Something went wrong on the server');
            }
            return data;
        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            throw error;
        }
    }

    // --- Authentication ---
    login(email, password) {
        return this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
    }

    signup(email, password, name) {
        return this.request('/auth/signup', {
            method: 'POST',
            body: JSON.stringify({ email, password, name })
        });
    }

    // --- Tasks ---
    getTasks() { return this.request('/tasks/get'); }
    addTask(taskData) { 
        return this.request('/tasks/add', { method: 'POST', body: JSON.stringify(taskData) }); 
    }

    // --- Planner ---
    generateSchedule() { return this.request('/planner/generate', { method: 'POST' }); }
    getSchedule() { return this.request('/planner/get'); }

    // --- ML Insights & Recommendations ---
    getInsights() { return this.request('/insights/'); }
    getRecommendations() { return this.request('/recommendations/'); }
    askCoach(question) { 
        return this.request('/recommendations/ask', { method: 'POST', body: JSON.stringify({ question }) }); 
    }
}

// Expose globally for app.js to use
window.api = new ApiService();
