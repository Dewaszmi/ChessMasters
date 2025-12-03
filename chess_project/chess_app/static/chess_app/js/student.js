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
  let bestMove = positions[currentIndex].best;
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
      showStats();
    }, 500);
  } else {
    setTimeout(function () {
      currentIndex++;
      if (currentIndex < totalTasks) {
        loadTask(currentIndex);
      } else {
        $result.html("Wszystkie zadania ukończone!");
      }
    }, 1500);
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
  let avgTime = sessionTotalTime / BATCH_SIZE;

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


// ======== MENU LOGIC ========

function startLevel(level) {
  // 1. Wybierz odpowiedni wycinek zadań z głównej listy
  // w CSV: 0-4 (Easy), 5-9 (Medium), 10-14 (Hard)
  currentLevel = level;

  if (level === 'easy') {
    positions = ALL_POSITIONS_SOURCE.slice(0, 5);
  } else if (level === 'medium') {
    positions = ALL_POSITIONS_SOURCE.slice(5, 10);
  } else if (level === 'hard') {
    if (ALL_POSITIONS_SOURCE.length < 15) {
      alert("Za mało zadań w pliku CSV! Dodaj więcej wierszy.");
      return;
    }
    positions = ALL_POSITIONS_SOURCE.slice(10, 15);
  }

  // 2. Zresetuj zmienne gry
  totalTasks = positions.length;
  currentIndex = 0;
  sessionSolved = 0;
  sessionCorrect = 0;
  sessionTotalTime = 0;

  // 3. Przełącz widok (Ukryj Menu, Pokaż Grę)
  $("#level-menu").hide();
  $("#game-container").show();
  $("#back-btn").show();

  // 4. Załaduj pierwsze zadanie z wybranego pakietu
  board.resize();
  loadTask(0);
}

function showMenu() {
  $("#game-container").hide();
  $("#back-btn").hide();
  $("#stats-modal").hide();
  $("#level-menu").show();
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + "=")) {
        cookieValue = cookie.substring(name.length + 1);
        break;
      }
    }
  }
  return cookieValue;
}
