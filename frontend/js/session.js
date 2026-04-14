/**
 * Session Module
 * Manages authentication token storage and retrieval
 */

const SESSION = {
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
};
