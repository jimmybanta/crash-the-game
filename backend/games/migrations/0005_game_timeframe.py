# Generated by Django 5.1.1 on 2024-09-05 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0004_remove_game_total_dollar_cost_game_word_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='timeframe',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
