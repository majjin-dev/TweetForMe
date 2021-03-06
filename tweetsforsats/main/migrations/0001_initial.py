# Generated by Django 4.0.3 on 2022-03-27 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Balances',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(db_index=True, max_length=66, unique=True)),
                ('pending', models.IntegerField()),
                ('available', models.IntegerField()),
                ('withdrawn', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Tweet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(db_index=True, max_length=66, unique=True)),
                ('twitter_id', models.CharField(max_length=25, unique=True)),
                ('created', models.DateTimeField(auto_now=True)),
                ('stake', models.IntegerField(default=100)),
            ],
        ),
    ]
