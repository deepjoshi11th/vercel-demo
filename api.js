/**
 * API Module
 * Handles HTTP requests with authentication
 */

const API = {
    baseURL: window.location.origin,

    async call(endpoint, options = {}) {
        const token = SESSION.getToken();
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
                SESSION.clearToken();
                throw new Error('Session expired. Please login again.');
            }

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || `API Error: ${response.status}`);
            }

            return response.json();
        } catch (error) {
            throw error;
        }
    },

    async fetchAllData() {
        return this.call('/api/data');
    },

    async fetchItem(itemId) {
        if (!itemId) {
            throw new Error('Item ID is required');
        }
        return this.call(`/api/items/${itemId}`);
    },

    async getProfileDetails() {
        return this.call('/api/profile-details');
    },

    async updateProfileDetails(sensitivePart) {
        if (!sensitivePart) {
            throw new Error('Sensitive part is required');
        }
        return this.call('/api/profile-details', {
            method: 'POST',
            body: JSON.stringify({ sensitive_part: sensitivePart }),
        });
    },
};
