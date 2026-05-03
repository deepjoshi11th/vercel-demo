const GAME_UI = {
    // DOM elements
    heroSection: null,
    protectedContent: null,
    questionContainer: null,
    optionsContainers: null,
    optButtons: null,
    optTags: null,
    downloadSection:null,
    downloadButton: null,
    judgementTitle: null,
    judgementJustification: null,
    
    async init() {
        this.heroSection = document.querySelector('.hero');
        this.protectedContent = document.querySelector('#protected-content');
        this.downloadSection = document.querySelector('#download-section');
        this.questionContainer = document.querySelector('#question');
        this.optButtons = document.querySelectorAll('[id^=opt-btn]');
        this.optionsContainers = document.querySelectorAll('[id^=opt-text]');
        this.optTags = document.querySelectorAll('.tagline');
        this.judgementTitle = document.querySelector('#j-title');
        this.judgementJustification = document.querySelector('#j-just');
        this.confirmityCheckbox = document.querySelector('#confirmity-checkbox');
        this.downloadButton = document.querySelector('#download-btn');
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
        this.showProtectedContent();
        this.downloadSection.style.display = 'block';
    },

    showJudgement(judgement) {
        if (!this.confirmityCheckbox.checked) {
           this.judgementTitle.textContent = judgement['critical']['title'];
            this.judgementJustification.textContent = judgement['critical']['justification'];
        } else {
            this.judgementTitle.textContent = judgement['comformity']['title'];
            this.judgementJustification.textContent = judgement['comformity']['justification'];
        }

    },

    updateQuestion(question, options) {
        this.questionContainer.textContent = question;
        options.forEach((option, index) => {
            let oIndex = option.indexOf('(');
            let cIndex = option.indexOf(')');
            if (oIndex !== -1 && cIndex !== -1 && cIndex > oIndex) {
                this.optTags[index].textContent = option.substring(oIndex + 1, cIndex);
                const optContainer = this.optionsContainers[index];
                optContainer.textContent = option.substring(0, oIndex).trim();
            } else {
                this.optTags[index].textContent = 'Option ' + (index + 1);
                const optContainer = this.optionsContainers[index];
                optContainer.textContent = option;
            }
        });
    }
};