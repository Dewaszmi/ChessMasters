import csv
from tkinter import filedialog


def parse_fen_csv():
    """Load a CSV of FEN positions and best moves."""
    path = filedialog.askopenfilename(
        title="Select CSV file", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )
    if not path:
        return None
    positions = []
    with open(path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            fen = row["fen"].strip()
            best_move = row["best"].strip()
            positions.append((fen, best_move))
    return positions
