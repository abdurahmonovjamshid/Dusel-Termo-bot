# Generated by Django 5.1.1 on 2024-09-20 06:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0009_remove_report_is_finished'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='bot.tguser'),
            preserve_default=False,
        ),
    ]
