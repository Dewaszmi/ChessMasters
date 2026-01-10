import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chess_project.settings')
django.setup()

from chess_app.models import Module, StudentModule, StudentTaskResult

def run():
    print("🧹 Usuwanie starych danych treningowych...")
    # Czyścimy wyniki, bo są powiązane z modułami
    StudentTaskResult.objects.all().delete()
    StudentModule.objects.all().delete()
    # Usuwamy same moduły
    Module.objects.all().delete()
    print("✨ Baza modułów jest teraz pusta. Możemy zaczynać od nowa!")

if __name__ == '__main__':
    run()