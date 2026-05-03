const GAME = {
    currentQuestionId: null,
    gameId: null,
    text: null,
    options: null,
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
                const answer = index;
                await this.submitAnswer(questionId, answer);
            });
        });
        GAME_UI.downloadButton.addEventListener('click', this.updateJudgement);
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

    async submitAnswer(questionId, answerIndex) {
        try {
            await GAME_API.submitAnswer(questionId, this.options[answerIndex]);
            let response = await GAME_API.generateNewQuestion(this.gameId);
            this.updateQuestion(response['data']);
        } catch (error) {
            console.error('Error submitting answer:', error);
        }
    },

    updateQuestion(questionData) {
        this.currentQuestionId = questionData['id'];
        this.text = questionData['text'];
        this.options = questionData['options'];
        if (questionData['cont']) {
            GAME.currentQuestionId = questionData['id'];
            GAME_UI.updateQuestion(this.text, this.options);
            GAME_UI.showProtectedContent();
        } else {
            GAME_UI.showResultUI();
        }
    },

    async updateJudgement() {
        const judgement =  await GAME.callJudgement();
        GAME_UI.showJudgement(judgement);
    },

    async callJudgement() {
        try {
            const response = await GAME_API.getJudgement(this.gameId);
            return response['data'];
        } catch (error) {
            console.error('Error getting judgement:', error);
            return null;
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    GAME.init();
});