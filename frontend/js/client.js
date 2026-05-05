
const CLIENT = {

    baseURL: window.location.origin,
    STORAGE_KEY: 'auth_token',

    getToken() {
        return localStorage.getItem(this.STORAGE_KEY);
    },

    setToken(token) {
        localStorage.setItem(this.STORAGE_KEY, token);
    },

    clearToken() {
        localStorage.removeItem(this.STORAGE_KEY);
    },

    isAuthenticated() {
        return !!this.getToken();
    },

    async call(endpoint, options = {}, responseType = 'json') {
        const token = this.getToken();
        const headers = {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` }),
            ...options.headers,
        };
        
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                ...options,
                headers,
            });
            
            if (response.status === 401) {
                // Token invalid or expired
                this.clearToken();
                throw new Error('Session expired. Please login again.');
            }
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || `API Error: ${response.status}`);
            }
                      
            if (responseType === 'blob') {
                return response.blob();
            }
            
            return response.json();
        } catch (error) {
            throw error;
        }
    }
};
    