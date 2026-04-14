/**
 * Main Application Module
 * Orchestrates authentication and UI
 */

const APP = {
    async init() {
        // Initialize UI and attach event listeners
        UI.init();
        this.setupEventListeners();

        // Check if user is already logged in
        if (SESSION.isAuthenticated()) {
            await this.loadUserProfile();
        } else {
            UI.showAuthUI();
        }
    },

    setupEventListeners() {
        // Form toggle buttons
        UI.showSignupBtn.addEventListener('click', (e) => {
            e.preventDefault();
            UI.toggleSignupForm();
        });

        UI.showLoginBtn.addEventListener('click', (e) => {
            e.preventDefault();
            UI.toggleLoginForm();
        });

        UI.loginLink.addEventListener('click', (e) => {
            e.preventDefault();
            UI.showAuthUI();
            UI.toggleLoginForm();
        });

        // Form submissions
        UI.loginFormElement.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });

        UI.signupFormElement.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSignup();
        });

        // Logout button
        UI.logoutBtn.addEventListener('click', () => {
            this.handleLogout();
        });

        // Data fetch buttons
        UI.fetchAllDataBtn.addEventListener('click', () => {
            this.fetchAllData();
        });

        UI.fetchItemBtn.addEventListener('click', () => {
            this.fetchItemById();
        });

        // Allow Enter key in item ID input to fetch
        UI.itemIdInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.fetchItemById();
            }
        });

        // Profile details handlers
        UI.profileDetailsForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSaveProfileDetails();
        });

        UI.viewProfileDetailsBtn.addEventListener('click', () => {
            this.handleViewProfileDetails();
        });
    },

    async handleLogin() {
        const { email, password } = UI.getLoginFormValues();

        if (!email || !password) {
            UI.showError('Please fill in all fields');
            return;
        }

        const result = await AUTH.login(email, password);

        if (result.success) {
            UI.setUserEmail(result.user.email);
            UI.showProtectedUI();
            UI.clearForms();
        } else {
            UI.showError(result.error);
        }
    },

    async handleSignup() {
        const { email, password, confirmPassword } = UI.getSignupFormValues();

        if (!email || !password || !confirmPassword) {
            UI.showError('Please fill in all fields');
            return;
        }

        const result = await AUTH.signup(email, password, confirmPassword);

        if (result.success) {
            UI.setUserEmail(result.user.email);
            UI.showProtectedUI();
            UI.clearForms();
        } else {
            UI.showError(result.error);
            if (result.error.includes('Check your email')) {
                UI.toggleLoginForm();
            }
        }
    },

    async handleLogout() {
        if (confirm('Are you sure you want to logout?')) {
            await AUTH.logout();
            UI.showAuthUI();
            UI.toggleLoginForm();
            UI.clearForms();
        }
    },

    async loadUserProfile() {
        try {
            const user = await AUTH.getCurrentUser();
            UI.setUserEmail(user.email);
            UI.showProtectedUI();
        } catch (error) {
            // Token is invalid
            SESSION.clearToken();
            UI.showAuthUI();
            UI.showError('Session expired. Please login again.');
        }
    },

    async fetchAllData() {
        UI.showLoading();

        try {
            const data = await API.fetchAllData();
            UI.displayData(data);
        } catch (error) {
            UI.displayData({ error: error.message });
        }
    },

    async fetchItemById() {
        const itemId = UI.getItemId();

        if (!itemId) {
            UI.showError('Please enter an item ID');
            return;
        }

        UI.showLoading();

        try {
            const data = await API.fetchItem(itemId);
            UI.displayData(data);
        } catch (error) {
            UI.displayData({ error: error.message });
        }
    },

    async handleSaveProfileDetails() {
        const sensitivePart = UI.getProfileDetailsInput();

        if (!sensitivePart) {
            UI.showError('Please enter profile details');
            return;
        }

        try {
            const result = await API.updateProfileDetails(sensitivePart);
            if (result.success) {
                UI.showError('Profile details saved successfully!');
                UI.clearProfileDetailsInput();
                // Refresh the display if it's open
                if (UI.profileDetailsDisplay.style.display === 'block') {
                    await this.handleViewProfileDetails();
                }
            }
        } catch (error) {
            UI.showError(error.message);
        }
    },

    async handleViewProfileDetails() {
        try {
            const result = await API.getProfileDetails();
            if (result.success) {
                UI.displayProfileDetails(result.data);
            }
        } catch (error) {
            UI.showError(error.message);
        }
    },
};

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    APP.init();
});
