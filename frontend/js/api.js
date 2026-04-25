/**
 * API Module
 * Handles HTTP requests with authentication
 */

const API = {
    async fetchAllData() {
        return CLIENT.call('/api/data');
    },

    async fetchItem(itemId) {
        if (!itemId) {
            throw new Error('Item ID is required');
        }
        return CLIENT.call(`/api/items/${itemId}`);
    },

    async getProfileDetails() {
        return CLIENT.call('/api/profile-details');
    },

    async updateProfileDetails(sensitivePart) {
        if (!sensitivePart) {
            throw new Error('Sensitive part is required');
        }
        return CLIENT.call('/api/profile-details', {
            method: 'POST',
            body: JSON.stringify({ sensitive_part: sensitivePart }),
        });
    },

    async generateQR(data) {
        const token = SESSION.getToken();
        const headers = {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` }),
        };

        const response = await fetch(`${this.baseURL}/api/qr`, {
            method: 'POST',
            headers,
            body: JSON.stringify(data),
        });

        if (response.status === 401) {
            SESSION.clearToken();
            throw new Error('Session expired. Please login again.');
        }

        if (!response.ok) {
            const error = await response.text();
            throw new Error(error || `API Error: ${response.status}`);
        }

        return response.blob();
    },
};
