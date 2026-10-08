from django.db import migrations


class Migration(migrations.Migration):
    """
    No-op: TeacherStudent уже создаётся моделью 0001_initial в финальном виде.
    Операции здесь намеренно пустые — оставлено для совместимости с базами,
    где эта миграция уже отмечена как применённая.
    """

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = []
