# Generated by Django 5.0.3 on 2024-04-01 22:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CareerLink', '0018_alter_experience_end_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='education',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='education',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]