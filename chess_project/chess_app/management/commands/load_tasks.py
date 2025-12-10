import csv
import os
from django.conf import settings
from django.core.management.base import BaseCommand
from chess_app.models import Task

class Command(BaseCommand):
    help = 'Ładuje zadania z CSV do bazy danych'

    def handle(self, *args, **kwargs):
        # Ścieżka do Twojego pliku CSV
        file_path = os.path.join(settings.BASE_DIR, "chess_app", "data", "sample_task_batch.csv")
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR('Brak pliku CSV!'))
            return

        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                # Sprawdzamy po FEN czy zadanie już jest, żeby nie dublować
                if not Task.objects.filter(fen=row['fen']).exists():
                    Task.objects.create(
                        fen=row['fen'],
                        correct_move=row['best'],  # W CSV kolumna nazywa się 'best'
                        level="easy"
                    )
                    count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Sukces! Dodano {count} nowych zadań do bazy.'))