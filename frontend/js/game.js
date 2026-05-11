const GAME = {
    currentQuestionId: null,
    gameId: null,
    text: null,
    options: null,
    hasExistingGame: false,
    lastAction: null, // Track last action for retry
    lastActionData: null, // Store data for retry
    
    async init() {
        await GAME_UI.init();
        this.setupEventListeners();

        if (AUTH.isAuthenticated()) {
            await this.showGameMenu();
        } else {
            GAME_UI.showDefaultUI();
        }
    },

    setupEventListeners() {
        GAME_UI.optButtons.forEach((button, index) => {
            button.addEventListener('click', async () => {
                const questionId = this.currentQuestionId;
                const answer = index;
                await this.submitAnswer(questionId, answer);
            });
        });
        GAME_UI.downloadButton.addEventListener('click', this.updateJudgement);
        GAME_UI.startNewGameBtn.addEventListener('click', () => this.deleteAndStartNewGame());
        GAME_UI.resumeGameBtn.addEventListener('click', () => this.resumeGame());
        GAME_UI.backToMenuBtn.addEventListener('click', () => this.deleteAndBackToMenu());
        GAME_UI.retryBtn.addEventListener('click', () => this.retryLastAction());
        GAME_UI.errorBackBtn.addEventListener('click', () => this.deleteAndBackToMenu());
    },

    async showGameMenu() {
        try {
            const response = await GAME_API.getGameIDForUser();
            this.hasExistingGame = response.data ? true : false;
            GAME_UI.showMenu(this.hasExistingGame);
        } catch (error) {
            console.error('Error checking for existing game:', error);
            GAME_UI.showMenu(false);
        }
    },

    async startNewGame() {
        try {
            const response = await GAME_API.createGame();
            this.gameId = response['data']['gameid'];
            await this.loadNextQuestion();
            GAME_UI.showGameUI();
        } catch (error) {
            console.error('Error starting new game:', error);
            GAME_UI.showDefaultUI();
        }
    },

    async deleteAndStartNewGame() {
        try {
            let response = await GAME_API.getGameIDForUser();
            if (response['success'] && response['data'] != null) {
                this.gameId = response['data']['gameId'];
                await GAME_API.deleteGame(this.gameId);
                console.log('Existing game deleted');
            }
            // Now start a new game
            await this.startNewGame();
        } catch (error) {
            console.error('Error deleting game and starting new:', error);
            // Still try to start a new game even if deletion fails
            await this.startNewGame();
        }
    },

    async resumeGame() {
        try {
            let response = await GAME_API.getGameIDForUser();
            this.gameId = response['data']['gameId'];
            await this.loadNextQuestion();
            GAME_UI.showGameUI();
        } catch (error) {
            console.error('Error resuming game:', error);
            GAME_UI.showDefaultUI();
        }
    },

    async deleteAndBackToMenu() {
        try {
            // Delete current game if one is active
            if (this.gameId) {
                await GAME_API.deleteGame(this.gameId);
                console.log('Current game deleted');
                this.gameId = null;
            }
            // Go back to menu
            await this.showGameMenu();
        } catch (error) {
            console.error('Error deleting game and returning to menu:', error);
            // Still go back to menu even if deletion fails
            await this.showGameMenu();
        }
    },

    async launchGame() {
        try {
            let response = await GAME_API.getGameIDForUser();
            if (!response.data) {
                response = await GAME_API.createGame(); 
            }
            this.gameId = response['data']['gameId'];
            let questionData = await GAME_API.generateNewQuestion(this.gameId);
            this.updateQuestion(questionData['data']);
        } catch (error) {
            console.error('Error launching game:', error);
            GAME_UI.showDefaultUI();
        }
    },

    async loadNextQuestion() {
        try {
            this.lastAction = 'loadNextQuestion';
            this.lastActionData = {};
            GAME_UI.showLoading();
            let questionData = await GAME_API.generateNewQuestion(this.gameId);
            GAME_UI.hideLoading();
            this.updateQuestion(questionData['data']);
        } catch (error) {
            console.error('Error loading question:', error);
            GAME_UI.showError('Failed to load the next question. Please try again.');
        }
    },

    async submitAnswer(questionId, answerIndex) {
        try {
            this.lastAction = 'submitAnswer';
            this.lastActionData = { questionId, answerIndex };
            GAME_UI.showLoading();
            await GAME_API.submitAnswer(questionId, this.options[answerIndex]);
            let response = await GAME_API.generateNewQuestion(this.gameId);
            GAME_UI.hideLoading();
            this.updateQuestion(response['data']);
        } catch (error) {
            console.error('Error submitting answer:', error);
            GAME_UI.showError('Failed to load the next question. Your answer has been recorded. Please try again.');
        }
    },

    updateQuestion(questionData) {
        this.currentQuestionId = questionData['id'];
        this.text = questionData['text'];
        this.options = questionData['options'];
        if (questionData['cont']) {
            GAME.currentQuestionId = questionData['id'];
            GAME_UI.updateQuestion(this.text, this.options);
            GAME_UI.showGameUI();
        } else {
            GAME_UI.showResultUI();
        }
    },

    async updateJudgement() {
        try {
            this.lastAction = 'updateJudgement';
            this.lastActionData = {};
            GAME_UI.showLoading();
            const judgement = await GAME.callJudgement();
            GAME_UI.hideLoading();
            GAME_UI.showJudgement(judgement);
        } catch (error) {
            console.error('Error getting judgement:', error);
            GAME_UI.showError('Failed to get judgement. Please try again.');
        }
    },

    async callJudgement() {
        try {
            const response = await GAME_API.getJudgement(this.gameId);
            return response['data'];
        } catch (error) {
            console.error('Error getting judgement:', error);
            return null;
        }
    },

    async retryLastAction() {
        if (this.lastAction === 'loadNextQuestion') {
            await this.loadNextQuestion();
        } else if (this.lastAction === 'submitAnswer') {
            const { questionId, answerIndex } = this.lastActionData;
            await this.submitAnswer(questionId, answerIndex);
        } else if (this.lastAction === 'updateJudgement') {
            await this.updateJudgement();
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    GAME.init();
});