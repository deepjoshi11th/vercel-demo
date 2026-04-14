/**
 * UI Module
 * Manages UI state and interactions
 */

const UI = {
    // DOM Elements
    authSection: null,
    protectedContent: null,
    userInfo: null,
    userEmail: null,
    logoutBtn: null,
    loginLink: null,
    loginForm: null,
    signupForm: null,
    loginFormElement: null,
    signupFormElement: null,
    showSignupBtn: null,
    showLoginBtn: null,
    fetchAllDataBtn: null,
    fetchItemBtn: null,
    itemIdInput: null,
    dataOutput: null,
    dataContent: null,
    loading: null,
    profileDetailsForm: null,
    profileDetailsInput: null,
    saveProfileDetailsBtn: null,
    viewProfileDetailsBtn: null,
    profileDetailsDisplay: null,

    // Initialize DOM elements
    init() {
        this.authSection = document.getElementById('auth-section');
        this.protectedContent = document.getElementById('protected-content');
        this.userInfo = document.getElementById('user-info');
        this.userEmail = document.getElementById('user-email');
        this.logoutBtn = document.getElementById('logout-btn');
        this.loginLink = document.getElementById('login-link');
        this.loginForm = document.getElementById('login-form');
        this.signupForm = document.getElementById('signup-form');
        this.loginFormElement = document.getElementById('login-form-element');
        this.signupFormElement = document.getElementById('signup-form-element');
        this.showSignupBtn = document.getElementById('show-signup-btn');
        this.showLoginBtn = document.getElementById('show-login-btn');
        this.fetchAllDataBtn = document.getElementById('fetch-all-data-btn');
        this.fetchItemBtn = document.getElementById('fetch-item-btn');
        this.itemIdInput = document.getElementById('item-id-input');
        this.dataOutput = document.getElementById('data-output');
        this.dataContent = document.getElementById('data-content');
        this.loading = document.getElementById('loading');
        this.errorMessage = document.getElementById('error-message');
        this.profileDetailsForm = document.getElementById('profile-details-form');
        this.profileDetailsInput = document.getElementById('sensitive-part-input');
        this.saveProfileDetailsBtn = document.getElementById('save-profile-details-btn');
        this.viewProfileDetailsBtn = document.getElementById('view-profile-details-btn');
        this.profileDetailsDisplay = document.getElementById('profile-details-display');
    },

    // Show authentication UI (not logged in)
    showAuthUI() {
        this.authSection.style.display = 'block';
        this.protectedContent.style.display = 'none';
        this.userInfo.style.display = 'none';
        this.loginLink.style.display = 'inline';
    },

    // Show protected content (logged in)
    showProtectedUI() {
        this.authSection.style.display = 'none';
        this.protectedContent.style.display = 'block';
        this.userInfo.style.display = 'inline-flex';
        this.loginLink.style.display = 'none';
    },

    // Toggle between login and signup forms
    toggleSignupForm() {
        this.loginForm.style.display = 'none';
        this.signupForm.style.display = 'block';
    },

    toggleLoginForm() {
        this.signupForm.style.display = 'none';
        this.loginForm.style.display = 'block';
    },

    // Set user email display
    setUserEmail(email) {
        this.userEmail.textContent = email;
    },

    // Clear form inputs
    clearForms() {
        this.loginFormElement.reset();
        this.signupFormElement.reset();
    },

    // Show data output
    displayData(data) {
        this.loading.style.display = 'none';
        this.dataContent.textContent = JSON.stringify(data, null, 2);
        this.dataOutput.style.display = 'block';
    },

    // Show error message
    showError(message) {
        if (this.errorMessage) {
            this.errorMessage.textContent = message;
            this.errorMessage.style.display = 'block';
            setTimeout(() => {
                this.errorMessage.style.display = 'none';
            }, 5000);
        } else {
            alert(message);
        }
    },

    // Show loading state
    showLoading() {
        this.loading.style.display = 'block';
        this.dataOutput.style.display = 'none';
    },

    // Get form values
    getLoginFormValues() {
        return {
            email: document.getElementById('login-email').value,
            password: document.getElementById('login-password').value,
        };
    },

    getSignupFormValues() {
        return {
            email: document.getElementById('signup-email').value,
            password: document.getElementById('signup-password').value,
            confirmPassword: document.getElementById('signup-confirm-password').value,
        };
    },

    getItemId() {
        return this.itemIdInput.value;
    },

    getProfileDetailsInput() {
        return this.profileDetailsInput.value;
    },

    setProfileDetailsInput(value) {
        this.profileDetailsInput.value = value;
    },

    clearProfileDetailsInput() {
        this.profileDetailsInput.value = '';
    },

    displayProfileDetails(data) {
        if (data) {
            this.profileDetailsDisplay.innerHTML = `
                <div class="profile-details-card">
                    <h4>Your Profile Details</h4>
                    <p class="detail-label">Sensitive Information:</p>
                    <p class="detail-value">${this.escapeHtml(data.sensitive_part)}</p>
                    <p class="detail-meta">ID: ${data.id}</p>
                </div>
            `;
        } else {
            this.profileDetailsDisplay.innerHTML = '<p style="color: #888888; text-align: center;">No profile details found</p>';
        }
        this.profileDetailsDisplay.style.display = 'block';
    },

    hideProfileDetails() {
        this.profileDetailsDisplay.style.display = 'none';
    },

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },
};
