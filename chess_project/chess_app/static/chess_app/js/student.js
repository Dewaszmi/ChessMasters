// ======== GLOBALS & STATE ========
let board = null;
let game = new Chess();
let currentTasks = [];
let currentTaskIndex = 0;
let currentModuleId = null;

// ======== HELPERS ========
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function removeHighlights() {
    $('#board .square-55d63').removeClass('highlight1-32417 highlight-capture');
}

// ======== CORE LOGIC ========
async function openModule(moduleId, title) {
    try {
        currentModuleId = moduleId;
        const response = await fetch(`/get-module-tasks/${moduleId}/`);
        if (!response.ok) throw new Error("Błąd pobierania zadań.");
        
        currentTasks = await response.json();
        
        if (currentTasks.length === 0) {
            alert("Ten moduł nie ma zadań.");
            return;
        }

        document.getElementById("module-list-view").style.display = "none";
        document.getElementById("game-view").style.display = "block";
        document.getElementById("active-title").innerText = title;
        
        currentTaskIndex = 0;
        loadTask();
    } catch (err) {
        alert(err.message);
    }
}

function loadTask() {
    const task = currentTasks[currentTaskIndex];
    document.getElementById("task-counter").innerText = `Zadanie ${currentTaskIndex + 1} z ${currentTasks.length}`;
    document.getElementById("result-message").innerText = "Twój ruch!";
    document.getElementById("result-message").className = "text-dark fw-bold fs-5";
    document.getElementById("next-btn").style.display = "none";
    
    game.load(task.fen);
    
    const config = {
        draggable: true,
        position: task.fen,
        onDragStart: onDragStart,
        onDrop: handleMove,
        onSnapEnd: onSnapEnd,
        pieceTheme: '/static/chess_app/img/chesspieces/wikipedia/{piece}.png'
    };
    
    if (board) board.destroy();
    board = Chessboard('board', config);
}

function onDragStart(source, piece, position, orientation) {
    // Prevent moving if game is over
    if (game.game_over()) return false;

    // Only allow player to move the pieces of the side whose turn it is
    if ((game.turn() === 'w' && piece.search(/^b/) !== -1) ||
        (game.turn() === 'b' && piece.search(/^w/) !== -1)) {
        return false;
    }

    // Highlight legal moves
    removeHighlights();
    let moves = game.moves({ square: source, verbose: true });
    if (moves.length === 0) return;

    $('#board .square-' + source).addClass('highlight1-32417');
    moves.forEach(move => {
        let $sq = $('#board .square-' + move.to);
        $sq.addClass('highlight1-32417');
        if (move.captured) $sq.addClass('highlight-capture');
    });
}

async function handleMove(source, target) {
    removeHighlights();
    const task = currentTasks[currentTaskIndex];
    
    // Validate move via chess.js
    const move = game.move({ from: source, to: target, promotion: 'q' });
    if (move === null) return 'snapback';

    const userMoveUCI = source + target; 
    const correctMove = task.solution.trim().toLowerCase();
    const isCorrect = (userMoveUCI === correctMove);

    // Update UI Feedback
    if (isCorrect) { 
        document.getElementById("result-message").innerText = "Brawo! Prawidłowy ruch.";
        document.getElementById("result-message").className = "text-success fw-bold fs-5";
    } else {
        document.getElementById("result-message").innerText = "Zły ruch! Poprawny to: " + task.solution;
        document.getElementById("result-message").className = "text-danger fw-bold fs-5";
    }

    board.draggable = false; // Lock board
    document.getElementById("next-btn").style.display = "inline-block";

    // Async save to backend
    try {
        await fetch('/save-result/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                module_id: currentModuleId,
                tasks_data: [{
                    task_id: task.id,
                    is_correct: isCorrect,
                    user_move: userMoveUCI
                }]
            })
        });
    } catch (err) {
        console.error("Błąd zapisu:", err);
    }
}

function onSnapEnd() {
    board.position(game.fen());
}

function nextTask() {
    currentTaskIndex++;
    if (currentTaskIndex < currentTasks.length) {
        loadTask();
    } else {
        alert("Moduł ukończony!");
        location.reload();
    }
}

// Handle window resize for chessboard responsiveness
$(window).on('resize', function() {
    if (board) board.resize();
});