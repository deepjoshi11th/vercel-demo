const GAME_UI = {
    // DOM elements
    heroSection: null,
    protectedContent: null,
    questionContainer: null,
    optionsContainers: null,
    optButtons: null,
    downloadSection:null,
    downloadButton: null,
    judgementCard: null,
    judgementText: null,
    
    async init() {
        this.heroSection = document.querySelector('.hero');
        this.protectedContent = document.querySelector('#protected-content');
        this.downloadSection = document.querySelector('#download-section');
        this.questionContainer = document.querySelector('#question');
        this.optButtons = document.querySelectorAll('[id^=opt-btn]');
        this.optionsContainers = document.querySelectorAll('[id^=opt-text]');
        this.judgementCard = document.querySelector('#judgement-card');
        this.judgementText = document.querySelector('#judgement');
    },

    showProtectedContent() {
        this.heroSection.style.display = 'none';
        this.protectedContent.style.display = 'block';
    },

    showDefaultUI() {
        this.heroSection.style.display = 'block';
        this.protectedContent.style.display = 'none';
    },

    showResultUI() {
        if (this.protectedContent.style.display === 'none') {
            this.downloadSection.style.display = 'block';
        }
        this.downloadSection.style.display = 'block';
    },

    showJudgement(judgement) {
        this.judgementText.textContent = judgement;
        this.judgementCard.style.display = 'block';
    },

    updateQuestion(question, options) {
        this.questionContainer.textContent = question;
        options.forEach((option, index) => {
            const optContainer = this.optionsContainers[index];
            optContainer.textContent = option;
        });
    }
};