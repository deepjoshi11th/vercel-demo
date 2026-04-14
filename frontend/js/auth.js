/**
 * Authentication Module
 * Handles signup, login, and logout operations
 */

const AUTH = {
    async signup(email, password, confirmPassword) {
        if (password !== confirmPassword) {
            return { success: false, error: 'Passwords do not match' };
        }

        if (password.length < 6) {
            return { success: false, error: 'Password must be at least 6 characters' };
        }

        try {
            const data = await API.call('/auth/signup', {
                method: 'POST',
                body: JSON.stringify({ email, password }),
            });

            if (data.session && data.session.access_token) {
                SESSION.setToken(data.session.access_token);
                return { success: true, user: data.user };
            } else {
                return {
                    success: false,
                    error: 'Signup successful! Check your email to confirm your account.'
                };
            }
        } catch (error) {
            return { success: false, error: error.message };
        }
    },

    async login(email, password) {
        if (!email || !password) {
            return { success: false, error: 'Email and password are required' };
        }

        try {
            const data = await API.call('/auth/login', {
                method: 'POST',
                body: JSON.stringify({ email, password }),
            });

            if (data.session && data.session.access_token) {
                SESSION.setToken(data.session.access_token);
                return { success: true, user: data.user };
            } else {
                return { success: false, error: 'Login failed' };
            }
        } catch (error) {
            return { success: false, error: error.message };
        }
    },

    async logout() {
        try {
            await API.call('/auth/logout', { method: 'POST' });
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            SESSION.clearToken();
        }
    },

    async getCurrentUser() {
        try {
            const user = await API.call('/auth/me');
            return user;
        } catch (error) {
            throw error;
        }
    },
};
