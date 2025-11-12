// ========================================
// Kategorie-Blitz Game Mode
// ========================================

let categoryGameState = {
    score: 0,
    correct: 0,
    wrong: 0,
    currentQuestion: null
};

// Category translations and emojis
const CATEGORY_INFO = {
    'Tier': { name: 'Tiere', emoji: '🦫' },
    'Essen': { name: 'Essen', emoji: '🍎' },
    'Familie': { name: 'Familie', emoji: '👨‍👩‍👧‍👦' },
    'Schule': { name: 'Schule', emoji: '📚' },
    'Körper': { name: 'Körper', emoji: '👤' },
    'Haus': { name: 'Haus', emoji: '🏠' },
    'Natur': { name: 'Natur', emoji: '🌳' },
    'Kleidung': { name: 'Kleidung', emoji: '👕' },
    'Fahrzeug': { name: 'Fahrzeuge', emoji: '🚗' },
    'Zeit': { name: 'Zeit', emoji: '⏰' },
    'Farbe': { name: 'Farben', emoji: '🎨' },
    'Other': { name: 'Andere', emoji: '📦' }
};

function startCategoryQuiz() {
    showScreen('categoryQuiz');
    categoryGameState = { score: 0, correct: 0, wrong: 0, currentQuestion: null };
    updateCategoryUI();
    loadNextCategoryQuestion();
}

async function loadNextCategoryQuestion() {
    try {
        const response = await fetch('/api/category-quiz');
        if (!response.ok) throw new Error('Failed to load question');

        const data = await response.json();
        categoryGameState.currentQuestion = data;

        document.getElementById('categoryWord').textContent = data.word;
        const stars = '\u2B50'.repeat(data.difficulty);
        document.getElementById('categoryDifficulty').textContent =
            `Schwierigkeit: ${stars}`;
        document.getElementById('categoryFeedback').textContent = '';

        // Display answer buttons with category options
        const buttonsContainer = document.getElementById('categoryButtons');
        buttonsContainer.innerHTML = '';

        data.options.forEach(category => {
            const button = document.createElement('button');
            button.className = 'btn-category';
            const info = CATEGORY_INFO[category] || { name: category, emoji: '📦' };
            button.innerHTML = `${info.emoji} ${info.name}`;
            button.onclick = () => checkCategoryAnswer(category);
            buttonsContainer.appendChild(button);
        });

    } catch (error) {
        console.error('Error loading category question:', error);
        document.getElementById('categoryFeedback').innerHTML =
            '\u274C Fehler beim Laden. <button onclick="loadNextCategoryQuestion()">Nochmal versuchen</button>';
    }
}

function checkCategoryAnswer(userAnswer) {
    const correct = categoryGameState.currentQuestion.category;
    const isCorrect = userAnswer === correct;
    const word = categoryGameState.currentQuestion.word;
    const correctInfo = CATEGORY_INFO[correct] || { name: correct, emoji: '📦' };

    if (isCorrect) {
        categoryGameState.score += categoryGameState.currentQuestion.difficulty * 10;
        categoryGameState.correct++;
        document.getElementById('categoryFeedback').innerHTML =
            `\u2705 Richtig! "${word}" gehört zu ${correctInfo.emoji} ${correctInfo.name}!`;
    } else {
        categoryGameState.wrong++;
        document.getElementById('categoryFeedback').innerHTML =
            `\u274C Falsch! "${word}" gehört zu ${correctInfo.emoji} ${correctInfo.name}.`;
    }

    updateCategoryUI();

    // Disable answer buttons temporarily
    document.querySelectorAll('.btn-category').forEach(btn => btn.disabled = true);

    // Load next question after delay
    setTimeout(loadNextCategoryQuestion, 2000);
}

function updateCategoryUI() {
    document.getElementById('categoryScore').textContent = categoryGameState.score;
    document.getElementById('categoryCorrect').textContent = categoryGameState.correct;
    document.getElementById('categoryWrong').textContent = categoryGameState.wrong;
}
