# Generated by Django 5.0.3 on 2024-04-01 22:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CareerLink', '0020_education_field_of_study'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='education',
            name='description',
        ),
    ]
