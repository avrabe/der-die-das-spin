// Game State
let gameState = {
    mode: null, // 'practice', 'timed', 'multiplayer'
    score: 0,
    sessionId: null,
    playerId: null,
    opponentScore: 0,
    timerInterval: null,
    timeRemaining: 120, // 2 minutes for timed mode
    currentWord: null,
    waitingInterval: null
};

// Screen Management
function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
    document.getElementById(screenId).classList.add('active');
}

function backToModeSelection() {
    clearIntervals();
    resetGameState();
    showScreen('modeSelection');
}

function clearIntervals() {
    if (gameState.timerInterval) {
        clearInterval(gameState.timerInterval);
        gameState.timerInterval = null;
    }
    if (gameState.waitingInterval) {
        clearInterval(gameState.waitingInterval);
        gameState.waitingInterval = null;
    }
}

function resetGameState() {
    gameState.score = 0;
    gameState.opponentScore = 0;
    gameState.timeRemaining = 120;
    gameState.currentWord = null;
    document.getElementById('score').textContent = '0';
    document.getElementById('genus').hidden = true;
    document.getElementById('nextButton').disabled = true;
}

// Practice Mode
function startPracticeMode() {
    gameState.mode = 'practice';
    resetGameState();
    showScreen('gameScreen');
    document.getElementById('timerDisplay').style.display = 'none';
    document.getElementById('player2Score').classList.add('hidden');
    loadJSON();
}

// Timed Challenge Mode
function startTimedMode() {
    gameState.mode = 'timed';
    resetGameState();
    gameState.timeRemaining = 120;
    showScreen('gameScreen');
    document.getElementById('timerDisplay').style.display = 'block';
    document.getElementById('player2Score').classList.add('hidden');
    startTimer();
    loadJSON();
}

function startTimer() {
    updateTimerDisplay();
    gameState.timerInterval = setInterval(() => {
        gameState.timeRemaining--;
        updateTimerDisplay();

        if (gameState.timeRemaining <= 0) {
            endTimedGame();
        }
    }, 1000);
}

function updateTimerDisplay() {
    const minutes = Math.floor(gameState.timeRemaining / 60);
    const seconds = gameState.timeRemaining % 60;
    document.getElementById('timerDisplay').textContent =
        `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

function endTimedGame() {
    clearIntervals();
    document.getElementById('finalScore').textContent = gameState.score;
    document.getElementById('multiplayerResults').classList.add('hidden');
    showScreen('resultsScreen');
}

// Multiplayer Functions
function showCreateSession() {
    showScreen('createSession');
}

function showJoinSession() {
    showScreen('joinSession');
}

async function createMultiplayerSession() {
    const playerName = document.getElementById('createPlayerName').value.trim();

    if (!playerName) {
        showError('Please enter your name');
        return;
    }

    try {
        const response = await fetch('/api/session/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                player_name: playerName,
                game_mode: 'multiplayer'
            })
        });

        if (!response.ok) throw new Error('Failed to create session');

        const session = await response.json();
        gameState.sessionId = session.session_id;
        gameState.playerId = session.player1_id;
        gameState.mode = 'multiplayer';

        document.getElementById('displaySessionId').textContent = session.session_id;
        showScreen('waitingScreen');

        // Poll for second player
        waitForOpponent();
    } catch (error) {
        showError('Failed to create game: ' + error.message);
    }
}

async function joinMultiplayerSession() {
    const playerName = document.getElementById('joinPlayerName').value.trim();
    const sessionId = document.getElementById('joinSessionId').value.trim();

    if (!playerName || !sessionId) {
        showError('Please enter both name and session ID');
        return;
    }

    try {
        const response = await fetch('/api/session/join', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                player_name: playerName
            })
        });

        if (!response.ok) throw new Error('Session not found');

        const session = await response.json();
        gameState.sessionId = session.session_id;
        gameState.playerId = session.player2_id;
        gameState.mode = 'multiplayer';

        startMultiplayerGame();
    } catch (error) {
        showError('Failed to join game: ' + error.message);
    }
}

function waitForOpponent() {
    gameState.waitingInterval = setInterval(async () => {
        try {
            const response = await fetch(`/api/session/${gameState.sessionId}`);
            const session = await response.json();

            if (session.player2_id) {
                clearInterval(gameState.waitingInterval);
                startMultiplayerGame();
            }
        } catch (error) {
            console.error('Error checking for opponent:', error);
        }
    }, 2000);
}

function startMultiplayerGame() {
    clearIntervals();
    resetGameState();
    showScreen('gameScreen');
    document.getElementById('timerDisplay').style.display = 'none';
    document.getElementById('player2Score').classList.remove('hidden');
    loadJSON();

    // Start polling for opponent's score
    gameState.waitingInterval = setInterval(updateMultiplayerScores, 3000);
}

async function updateMultiplayerScores() {
    try {
        const response = await fetch(`/api/session/${gameState.sessionId}`);
        const session = await response.json();

        // Update opponent's score
        const isPlayer1 = session.player1_id === gameState.playerId;
        gameState.opponentScore = isPlayer1 ? session.player2_score : session.player1_score;
        document.getElementById('opponentScore').textContent = gameState.opponentScore;
    } catch (error) {
        console.error('Error updating scores:', error);
    }
}

function copySessionId() {
    const sessionId = document.getElementById('displaySessionId').textContent;
    navigator.clipboard.writeText(sessionId).then(() => {
        const btn = event.target;
        const originalText = btn.textContent;
        btn.textContent = 'Copied!';
        setTimeout(() => btn.textContent = originalText, 2000);
    });
}

function cancelMultiplayer() {
    clearIntervals();
    backToModeSelection();
}

function quitGame() {
    if (gameState.mode === 'timed') {
        endTimedGame();
    } else if (gameState.mode === 'multiplayer') {
        endMultiplayerGame();
    } else {
        backToModeSelection();
    }
}

function endMultiplayerGame() {
    clearIntervals();
    document.getElementById('finalScore').textContent = gameState.score;
    document.getElementById('opponentFinalScore').textContent = gameState.opponentScore;
    document.getElementById('multiplayerResults').classList.remove('hidden');

    const winnerText = document.getElementById('winnerText');
    if (gameState.score > gameState.opponentScore) {
        winnerText.textContent = '🎉 You Win!';
        winnerText.className = 'winner-announcement win';
    } else if (gameState.score < gameState.opponentScore) {
        winnerText.textContent = 'Opponent Wins';
        winnerText.className = 'winner-announcement lose';
    } else {
        winnerText.textContent = "It's a Tie!";
        winnerText.className = 'winner-announcement tie';
    }

    showScreen('resultsScreen');
}

// Core Game Logic
function loadJSON() {
    const xhr = new XMLHttpRequest();
    xhr.open("GET", "/api/entry.json", true);
    xhr.onload = function () {
        if (xhr.status === 200) {
            try {
                const data = JSON.parse(xhr.responseText);
                if (data && data.length > 0) {
                    gameState.currentWord = data[0];
                    displayWord(data[0]);
                    document.getElementById('nextButton').disabled = true;
                }
            } catch (e) {
                showError("Error parsing response");
            }
        } else {
            showError("Error loading word");
        }
    };
    xhr.onerror = function () {
        showError("Network error");
    };
    xhr.send();
}

function displayWord(entry) {
    // Set the correct article
    let correctArticle;
    if (entry.genus === "m") {
        correctArticle = "Der";
    } else if (entry.genus === "f") {
        correctArticle = "Die";
    } else if (entry.genus === "n") {
        correctArticle = "Das";
    }

    document.getElementById("genus").textContent = correctArticle;
    document.getElementById("genus").className = "genus";
    document.getElementById("genus").hidden = true;
    document.getElementById("nominativ_singular").innerHTML = "&nbsp;" + entry.nominativ_singular;

    // Reset button states
    document.querySelectorAll('.artikel-btn').forEach(btn => {
        btn.disabled = false;
        btn.classList.remove('correct', 'incorrect');
    });
}

async function reveal(artikel) {
    const genusEl = document.getElementById("genus");
    const correctArticle = genusEl.textContent;
    const isCorrect = artikel === correctArticle;

    // Disable all buttons after answer
    document.querySelectorAll('.artikel-btn').forEach(btn => btn.disabled = true);

    // Show visual feedback
    genusEl.hidden = false;
    if (isCorrect) {
        genusEl.className = "genus correct";
        gameState.score++;
        document.getElementById("score").textContent = gameState.score;

        // Submit score for multiplayer
        if (gameState.mode === 'multiplayer') {
            await submitAnswer(true);
        }
    } else {
        genusEl.className = "genus incorrect";

        if (gameState.mode === 'multiplayer') {
            await submitAnswer(false);
        }
    }

    // Enable next button
    document.getElementById('nextButton').disabled = false;
}

async function submitAnswer(correct) {
    try {
        await fetch(`/api/session/${gameState.sessionId}/answer`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                player_id: gameState.playerId,
                correct: correct
            })
        });
    } catch (error) {
        console.error('Error submitting answer:', error);
    }
}

function showError(message) {
    const errorEl = document.getElementById("error");
    errorEl.textContent = message;
    errorEl.style.display = 'block';
    setTimeout(() => {
        errorEl.style.display = 'none';
    }, 3000);
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    showScreen('modeSelection');
});
