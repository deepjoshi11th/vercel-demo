const GAME = {
    currentQuestionId: null,
    async init() {
        GAME_UI.init();
        GAME.setupEventListeners();

        if (AUTH.isAuthenticated()) {
            await this.launchGame();
        } else {
            GAME_UI.showDefaultUI();
        }
    },

    setupEvemtListeners() {
        GAME_UI.optButtons.forEach((button, index) => {
            button.addEventListener('click', async () => {
                const questionId = this.currentQuestionId;
                const answer = index; // Assuming options are indexed from 0
                await this.submitAnswer(questionId, answer);
            });
        });
    },

    async launchGame() {
        try {
            let gameId = await GAME_API.getGameIDForUser();
            if (!gameId) {
                gameId = await GAME_API.createGame();
            }
            let questionData = await GAME_API.generateNewQuestion(gameId);
            GAME.currentQuestionId = questionData.id;
            GAME_UI.updateQuestion(questionData.question, questionData.options);
            GAME_UI.showProtectedContent();
        } catch (error) {
            console.error('Error launching game:', error);
            GAME_UI.showDefaultUI();
        }
    },

    async submitAnswer(questionId, answer) {
        try {
            await GAME_API.submitAnswer(questionId, answer);
            let response = await GAME_API.generateNewQuestion(gameId);
            this.currentQuestionId = response.json().id;
            GAME_UI.updateQuestion(response.question, response.options);
        } catch (error) {
            console.error('Error submitting answer:', error);}
        }
    }

    

};

document.addEventListener('DOMContentLoaded', () => {
    GAME.init();
});