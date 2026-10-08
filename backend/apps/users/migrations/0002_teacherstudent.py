from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeacherStudent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('teacher', models.ForeignKey(
                    db_column='teacher_id',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='linked_students',
                    to='users.teacher',
                )),
                ('student', models.ForeignKey(
                    db_column='student_id',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='linked_teachers',
                    to='users.student',
                )),
            ],
            options={
                'verbose_name': 'Ученик учителя',
                'verbose_name_plural': 'Ученики учителей',
                'db_table': 'teacher_students',
                'unique_together': {('teacher', 'student')},
            },
        ),
    ]
