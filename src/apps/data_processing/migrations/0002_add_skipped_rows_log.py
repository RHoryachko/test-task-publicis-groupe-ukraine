# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("data_processing", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="datafile",
            name="skipped_rows_log",
            field=models.TextField(
                blank=True,
                default="",
                verbose_name="Лог пропущених рядків (Start > End)",
            ),
        ),
    ]
