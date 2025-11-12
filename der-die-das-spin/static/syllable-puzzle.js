// ========================================
// Silben-Puzzle Game Mode
// ========================================

let syllableGameState = {
    score: 0,
    correct: 0,
    wrong: 0,
    currentQuestion: null
};

function startSyllablePuzzle() {
    showScreen('syllablePuzzle');
    syllableGameState = { score: 0, correct: 0, wrong: 0, currentQuestion: null };
    updateSyllableUI();
    loadNextSyllableQuestion();
}

async function loadNextSyllableQuestion() {
    try {
        const response = await fetch('/api/syllable-quiz');
        if (!response.ok) throw new Error('Failed to load question');

        const data = await response.json();
        syllableGameState.currentQuestion = data;

        document.getElementById('syllableWord').textContent = data.word;
        const stars = '\u2B50'.repeat(data.difficulty);
        document.getElementById('syllableDifficulty').textContent =
            `Schwierigkeit: ${stars}`;
        document.getElementById('syllableFeedback').textContent = '';

        // Enable answer buttons
        document.querySelectorAll('.btn-answer').forEach(btn => btn.disabled = false);

    } catch (error) {
        console.error('Error loading syllable question:', error);
        document.getElementById('syllableFeedback').innerHTML =
            '\u274C Fehler beim Laden. <button onclick="loadNextSyllableQuestion()">Nochmal versuchen</button>';
    }
}

function checkSyllableAnswer(userAnswer) {
    const correct = syllableGameState.currentQuestion.syllable_count;
    const isCorrect = userAnswer === correct;
    const word = syllableGameState.currentQuestion.word;
    const silben = correct > 1 ? 'n' : '';

    // Split word into syllables for display
    const syllables = splitIntoSyllables(word, correct);
    const syllableDisplay = syllables.join(' • ');

    if (isCorrect) {
        syllableGameState.score += syllableGameState.currentQuestion.difficulty * 10;
        syllableGameState.correct++;
        document.getElementById('syllableFeedback').innerHTML =
            `\u2705 Richtig! "${word}" hat ${correct} Silbe${silben}!<br/>
            <span class="syllable-breakdown">${syllableDisplay}</span> \uD83E\uDDAB`;
    } else {
        syllableGameState.wrong++;
        document.getElementById('syllableFeedback').innerHTML =
            `\u274C Falsch! "${word}" hat ${correct} Silbe${silben}.<br/>
            <span class="syllable-breakdown">${syllableDisplay}</span>`;
    }

    updateSyllableUI();

    // Disable answer buttons temporarily
    document.querySelectorAll('.btn-answer').forEach(btn => btn.disabled = true);

    // Load next question after delay
    setTimeout(loadNextSyllableQuestion, 2500);
}

function splitIntoSyllables(word, syllableCount) {
    // Simple heuristic syllable splitting for German
    const vowels = 'aeiouäöüyAEIOUÄÖÜY';
    const syllables = [];
    let currentSyllable = '';
    let vowelCount = 0;

    for (let i = 0; i < word.length; i++) {
        const char = word[i];
        const isVowel = vowels.includes(char);

        // Check for diphthongs (ei, au, eu, etc.)
        const isDiphthong = i < word.length - 1 &&
            vowels.includes(char) &&
            vowels.includes(word[i + 1]) &&
            (char.toLowerCase() + word[i + 1].toLowerCase()).match(/ei|ai|au|eu|äu|ie|oi|ui/);

        currentSyllable += char;

        if (isVowel) {
            vowelCount++;

            // If we've found enough vowels and there's more word left
            if (vowelCount < syllableCount && i < word.length - 1) {
                // Look ahead to find a good break point
                let breakPoint = 0;
                for (let j = i + 1; j < word.length; j++) {
                    if (vowels.includes(word[j])) {
                        breakPoint = j;
                        break;
                    }
                }

                if (breakPoint > 0) {
                    // Include consonants before next vowel
                    const consonantsBetween = breakPoint - i - 1;
                    if (consonantsBetween > 0) {
                        currentSyllable += word.substring(i + 1, i + 1 + Math.floor(consonantsBetween / 2));
                        syllables.push(currentSyllable);
                        currentSyllable = word.substring(i + 1 + Math.floor(consonantsBetween / 2), breakPoint);
                        i = breakPoint - 1;
                    }
                }
            } else if (isDiphthong) {
                currentSyllable += word[i + 1];
                i++;
            }
        }
    }

    if (currentSyllable) {
        syllables.push(currentSyllable);
    }

    // If heuristic didn't work well, fall back to simple splitting
    if (syllables.length !== syllableCount) {
        return simpleSplit(word, syllableCount);
    }

    return syllables;
}

function simpleSplit(word, count) {
    // Fallback: just split evenly
    if (count === 1) return [word];

    const chunkSize = Math.ceil(word.length / count);
    const result = [];
    for (let i = 0; i < word.length; i += chunkSize) {
        result.push(word.substring(i, i + chunkSize));
    }
    return result.slice(0, count);
}

function updateSyllableUI() {
    document.getElementById('syllableScore').textContent = syllableGameState.score;
    document.getElementById('syllableCorrect').textContent = syllableGameState.correct;
    document.getElementById('syllableWrong').textContent = syllableGameState.wrong;
}
