# Generated by Django 5.0.3 on 2024-03-29 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CareerLink', '0007_offer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='offer',
            name='id',
        ),
        migrations.AddField(
            model_name='offer',
            name='offer_id',
            field=models.AutoField(default=1, primary_key=True, serialize=False),
            preserve_default=False,
        ),
    ]
