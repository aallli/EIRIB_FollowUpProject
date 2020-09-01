# Generated by Django 3.0.8 on 2020-09-01 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Knowledge_Management', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='limit',
            field=models.IntegerField(default=1, verbose_name='Limit'),
        ),
        migrations.AddField(
            model_name='activity',
            name='max_score',
            field=models.IntegerField(default=10, verbose_name='Maximum Score'),
        ),
    ]
