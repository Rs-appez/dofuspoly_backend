# Generated by Django 5.0.6 on 2024-11-10 02:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monopoly', '0004_alter_player_cards_alter_player_ownedcase'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='image',
            field=models.CharField(default='default.png', max_length=255),
        ),
    ]
