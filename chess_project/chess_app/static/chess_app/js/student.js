function pieceTheme(piece) {
  return "/static/chess_app/img/chesspieces/wikipedia/" + piece + ".png";
}

// ======== GLOBALS ========

const ALL_POSITIONS_SOURCE = window.POSITIONS;

let positions = [];

let totalTasks = 0;
let currentIndex = 0;
let moveMade = false;

// Statystyki
let sessionSolved = 0;
let sessionCorrect = 0;
const BATCH_SIZE = 5; // Pakiety zawsze po 5

// Czas
let taskStartTime = 0;
let sessionTotalTime = 0;

let board = null;
let game = null;

let $status = null;
let $fen = null;
let $pgn = null;
let $result = null;

let currentLevel = null;

// ======== INITIALIZE ========

function loadTask(index) {
  let pos = positions[index];

  game = new Chess(pos.fen);
  moveMade = false;

  board.position(pos.fen);
  updateStatus();

  $result.html("");

  document.getElementById("task-counter").innerText =
    "Task " + (index + 1) + " / " + totalTasks;

  // stoper
  taskStartTime = Date.now();
}

function removeHighlights() {
  $("#board .square-55d63").removeClass("highlight1-32417 highlight-capture");
}

function onDragStart(source, piece, position, orientation) {
  if (moveMade) return false;
  if (game.game_over()) return false;

  if ((game.turn() === "w" && piece.startsWith("b")) ||
    (game.turn() === "b" && piece.startsWith("w"))) {
    return false;
  }

  removeHighlights();

  let moves = game.moves({ square: source, verbose: true });
  $("#board .square-" + source).addClass("highlight1-32417");

  for (let move of moves) {
    let $sq = $("#board .square-" + move.to);
    $sq.addClass("highlight1-32417");
    if (move.captured) $sq.addClass("highlight-capture");
  }
}

function onDrop(source, target) {
  if (moveMade) return "snapback";

  let move = game.move({ from: source, to: target, promotion: "q" });

  if (move === null) return "snapback";

  let endTime = Date.now();
  let timeTaken = (endTime - taskStartTime) / 1000;
  sessionTotalTime += timeTaken;

  moveMade = true;
  updateStatus();

  let userMove = source + target;
  let bestMove = positions[currentIndex].correct_move;
  let isCorrect = (userMove === bestMove);

  sessionSolved++;
  if (isCorrect) {
    sessionCorrect++;
    $result.html("Dobrze! Najlepszy ruch: " + userMove);
    $result.css("color", "green");
  } else {
    $result.html("Błąd. Najlepszy ruch to: " + bestMove);
    $result.css("color", "red");
  }

  if (sessionSolved >= BATCH_SIZE) {
  setTimeout(function () {
    finishModule();
  }, 500);
} else {
  $("#next-btn").show();   
}
}

function onSnapEnd() {
  board.position(game.fen());
  removeHighlights();
}

function updateStatus() {
  let status = "";
  let moveColor = game.turn() === "w" ? "White" : "Black";

  if (game.in_checkmate()) {
    status = "Game over, " + moveColor + " is in checkmate.";
  } else if (game.in_draw()) {
    status = "Game over, drawn position";
  } else {
    status = moveColor + " to move";
    if (game.in_check()) status += ", " + moveColor + " is in check";
  }

  $status.html(status);
  $fen.html(game.fen());
  $pgn.html(game.pgn());
}

// ======== DOCUMENT READY ========

$(function () {
  $status = $("#status");
  $fen = $("#fen");
  $pgn = $("#pgn");
  $result = $("#result");

  board = Chessboard("board", {
    draggable: true,
    position: "start",
    pieceTheme: pieceTheme,
    onDragStart: onDragStart,
    onDrop: onDrop,
    onSnapEnd: onSnapEnd,
  });

  $(window).on("resize", board.resize);

});

function showStats() {
  // Obliczamy średnią
  let avgTime = (sessionTotalTime / BATCH_SIZE).toFixed(2);

  // Wysyłamy dane do bazy (views.py -> save_result)
  fetch("/save-result/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify({
      level: currentLevel,
      score: sessionCorrect,
      avg_time: avgTime
    }),
  })
  .then(response => {
      if (response.ok) {
          // Gdy dane się zapiszą, idziemy na stronę wyników
          window.location.href = "/results/";
      } else {
          alert("Błąd zapisu wyników!");
      }
  })
  .catch(error => console.error('Error:', error));
}


// ======== NOWA LOGIKA MODUŁÓW ========

let currentModuleId = null;

// Funkcja wywoływana po kliknięciu w moduł na liście (w HTML)
function openModule(moduleId, title) {
    currentModuleId = moduleId;

    // Pobieramy zadania dla tego konkretnego modułu z serwera
    fetch(`/get-module-tasks/${moduleId}/`)
        .then(response => response.json())
        .then(data => {
            // Podmieniamy listę zadań na te z bazy
            positions = data.tasks;
            totalTasks = positions.length;

            // Przełączamy widoki
            $("#module-list-view").hide(); // Ukrywamy tabelę
            $("#game-view").show();        // Pokazujemy szachownicę
            $("#active-title").text(title);

            // Resetujemy stan sesji
            currentIndex = 0;
            sessionSolved = 0;
            sessionCorrect = 0;
            sessionTotalTime = 0;

            board.resize();
            loadTask(0);
        })
        .catch(err => console.error("Błąd pobierania zadań:", err));
}

function nextTask() {
    $("#next-btn").hide();
    currentIndex++;

    if (currentIndex < totalTasks) {
        loadTask(currentIndex);
    } else {
        // Jeśli to było ostatnie zadanie, wyślij wynik do bazy
        finishModule();
    }
}

function finishModule() {
    let avgTime = (sessionTotalTime / totalTasks).toFixed(2);

    fetch("/save-result/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({
            module_id: currentModuleId,
            score: sessionCorrect,
            avg_time: avgTime
        }),
    })
    .then(response => {
        if (response.ok) {
            alert(`Ukończono moduł! Wynik: ${sessionCorrect}/${totalTasks}`);
            location.reload();
        } else {
            alert("Błąd zapisu wyników!");
        }
    });
}