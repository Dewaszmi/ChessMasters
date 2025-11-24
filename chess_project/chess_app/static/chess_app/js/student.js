function pieceTheme(piece) {
  return "/static/chess_app/img/chesspieces/wikipedia/" + piece + ".png";
}

// ======== GLOBALS ========

let positions = window.POSITIONS;      // full CSV list
let totalTasks = positions.length;
let currentIndex = 0;
let moveMade = false;

let board = null;
let game = null;

let $status = null;
let $fen = null;
let $pgn = null;
let $result = null;

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

  moveMade = true;
  updateStatus();

  let userMove = source + target;
  let bestMove = positions[currentIndex].best;

  if (userMove === bestMove) {
    $result.html("Correct! Best move: " + userMove);
  } else {
    $result.html("Incorrect. Best move was: " + bestMove);
  }

  // Load next task after 1.5 sec
  setTimeout(function() {
    currentIndex++;
    if (currentIndex < totalTasks) {
      loadTask(currentIndex);
    } else {
      $result.html("All tasks completed!");
    }
  }, 1500);
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

  loadTask(currentIndex);
});
