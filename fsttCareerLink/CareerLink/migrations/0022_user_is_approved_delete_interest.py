# Generated by Django 5.0.3 on 2024-04-02 01:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CareerLink', '0021_remove_education_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name='Interest',
        ),
    ]
