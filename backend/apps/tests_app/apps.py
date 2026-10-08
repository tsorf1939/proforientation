from django.apps import AppConfig


class TestsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.tests_app'
    verbose_name = 'Тесты'

    def ready(self):
        import apps.tests_app.signals  # noqa
