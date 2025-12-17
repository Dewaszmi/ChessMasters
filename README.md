# ChessMasters

### Installation

```bash
uv venv
uv pip install -r requirements.txt
```

or, if you don't have uv installed

```bash
pip install -r requirements.txt
```

### Testing

Go to project root (folder containing manage.py) and run:

```bash
pytest --reuse-db
```

or

```bash
python manage.py test chess_app.tests --keepdb
```

##### Additional info:

CSV files taken from https://www.kaggle.com/datasets/ancientaxe/mate-in-one-chess/data?select=train.csv
chessboard frontend implementation borrowed from https://www.chessboardjs.com/
