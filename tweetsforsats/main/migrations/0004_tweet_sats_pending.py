# Generated by Django 4.0.4 on 2022-05-20 02:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_alter_tweet_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='tweet',
            name='sats_pending',
            field=models.BooleanField(default=True),
        ),
    ]
