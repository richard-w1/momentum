# Generated by Django 5.1.6 on 2025-03-22 02:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0003_alter_habit_frequency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='habit',
            name='frequency',
            field=models.IntegerField(choices=[(1, 'Daily'), (7, 'Weekly'), (30, 'Monthly')]),
        ),
    ]
