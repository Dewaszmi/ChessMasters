from django.apps import AppConfig


class MyappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "chess_app"

    def ready(self):
        import chess_app.signals
