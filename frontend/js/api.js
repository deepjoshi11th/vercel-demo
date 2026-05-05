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
        if (!data) {
            throw new Error('Data is required to generate QR code');
        }
        return CLIENT.call('/api/qr', {
            method: 'POST',
            body: JSON.stringify(data),
        }, responseType = 'blob');
    },
};
