# Generated by Django 4.2.7 on 2023-11-09 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='joboffer',
            name='date_publication',
            field=models.CharField(max_length=100),
        ),
    ]
