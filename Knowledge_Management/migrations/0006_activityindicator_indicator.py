# Generated by Django 3.0.8 on 2020-09-03 08:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Knowledge_Management', '0005_committeemember'),
    ]

    operations = [
        migrations.CreateModel(
            name='Indicator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=2000, unique=True, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'Indicator',
                'verbose_name_plural': 'Indicators',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ActivityIndicator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Knowledge_Management.Activity', verbose_name='Activity')),
                ('indicator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Knowledge_Management.Indicator', verbose_name='Indicator')),
            ],
            options={
                'verbose_name': 'Activity Indicator',
                'verbose_name_plural': 'Activity Indicators',
                'ordering': ['activity', 'indicator'],
                'unique_together': {('activity', 'indicator')},
            },
        ),
    ]
