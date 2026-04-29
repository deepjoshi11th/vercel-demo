const GAME = {
    currentQuestionId: null,
    gameId: null,
    async init() {
        await GAME_UI.init();
        this.setupEventListeners();

        if (AUTH.isAuthenticated()) {
            await this.launchGame();
        } else {
            GAME_UI.showDefaultUI();
        }
    },

    setupEventListeners() {
        GAME_UI.optButtons.forEach((button, index) => {
            button.addEventListener('click', async () => {
                const questionId = this.currentQuestionId;
                const answer = GAME_UI.optionsContainers[index].textContent;
                await this.submitAnswer(questionId, answer);
            });
        });
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

    async submitAnswer(questionId, answer) {
        try {
            await GAME_API.submitAnswer(questionId, answer);
            let response = await GAME_API.generateNewQuestion(this.gameId);
            this.updateQuestion(response['data']);
        } catch (error) {
            console.error('Error submitting answer:', error);
        }
    },

    updateQuestion(questionData) {
        this.currentQuestionId = questionData['id'];
        if (questionData['cont']) {
            GAME.currentQuestionId = questionData['id'];
            GAME_UI.updateQuestion(questionData['text'], questionData['options']);
            GAME_UI.showProtectedContent();
        } else {
            GAME_UI.showResultUI();
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    GAME.init();
});