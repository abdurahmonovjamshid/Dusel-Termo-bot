# Generated by Django 5.1.1 on 2024-09-21 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0012_alter_report_defect_measure_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Machine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(verbose_name='apparat raqami')),
            ],
        ),
    ]
