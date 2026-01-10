import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chess_project.settings')
django.setup()

from django.contrib.auth.models import User
from chess_app.models import Profile, Group, StudentModule, StudentTaskResult


def run():
    print("🧹 Czyszczenie danych...")
    # Usuwamy wszystko co może blokować klucze
    StudentTaskResult.objects.all().delete()
    StudentModule.objects.all().delete()
    Group.objects.all().delete()

    # Usuwamy użytkowników oprócz superusera
    User.objects.exclude(is_superuser=True).delete()
    print("✨ Użytkownicy usunięci.")

    def create_safe_user(username, role):
        # get_or_create zapobiega błędom duplikacji
        user, created = User.objects.get_or_create(username=username)
        user.set_password(username)
        user.save()
        # update_or_create naprawia Twój błąd "IntegrityError"
        Profile.objects.update_or_create(user=user, defaults={'role': role})
        return user

    # 1. TRENERZY
    michal = create_safe_user("Michał", "trainer")
    maciej = create_safe_user("Maciej", "trainer")
    print("✅ Trenerzy stworzeni.")

    # 2. STUDENCI
    names = ["Adam", "Beata", "Cezary", "Damian", "Ewa", "Filip",
             "Grażyna", "Henryk", "Iwona", "Jacek", "Kasia", "Leon"]
    students = [create_safe_user(name, "student") for name in names]
    print("👤 Studenci stworzeni.")

    # 3. GRUPY
    groups = [
        ("Grupa A", michal, students[0:3]),
        ("Grupa B", michal, students[3:6]),
        ("Grupa C", maciej, students[6:9]),
        ("Grupa D", maciej, students[9:12]),
    ]

    for name, trainer, members in groups:
        g = Group.objects.create(name=name, trainer=trainer)
        g.students.set(members)
        print(f"👥 {name} przypisana do {trainer.username}")


if __name__ == '__main__':
    run()