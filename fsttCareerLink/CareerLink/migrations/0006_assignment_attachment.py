# Generated by Django 5.0.3 on 2024-03-27 05:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CareerLink', '0005_assignment_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='attachment',
            field=models.FileField(blank=True, null=True, upload_to='announcement_attachments/'),
        ),
    ]
