# Generated by Django 4.1.4 on 2024-01-16 08:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_emailtoken'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='patient_email',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]