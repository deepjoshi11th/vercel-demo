const GAME_API = {
    async createGame() {
        return CLIENT.call('/api/game', { method: 'POST'});
    },

    async getGameIDForUser() {
        return CLIENT.call('/api/game');
    },

    async generateNewQuestion(gameId) {
        if (!gameId) {
            throw new Error('Game ID is required');
        }
        return CLIENT.call(`/api/game/questions/generate/${gameId}`, { method: 'POST' });
    },

    async getAllQuestions(gameId) {
        if (!gameId) {
            throw new Error('Game ID is required');
        }
        return CLIENT.call(`/api/game/questions/${gameId}`);
    },

    async submitAnswer(questionId, answer) {
        if (!questionId) {
            throw new Error('Question ID is required');
        }
        if (!answer) {
            throw new Error('Answer is required');
        }
        return CLIENT.call(`/api/game/answer/${questionId}?answer=${encodeURIComponent(answer)}`, {
            method: 'PATCH',
        });
    },

    async getJudgement(gameId) {
        if (!gameId) {
            throw new Error('Game ID is required');
        }
        return CLIENT.call(`/api/game/judgement/${gameId}`);
    }
}