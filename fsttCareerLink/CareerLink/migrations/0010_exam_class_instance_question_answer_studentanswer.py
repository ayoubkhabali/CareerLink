# Generated by Django 5.0.3 on 2024-03-27 21:14

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CareerLink', '0009_remove_assignment_submission_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='class_instance',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='CareerLink.class'),
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('question_text', models.CharField(max_length=255)),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CareerLink.exam')),
            ],
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('answer_text', models.CharField(max_length=255)),
                ('is_correct', models.BooleanField(default=False)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CareerLink.question')),
            ],
        ),
        migrations.CreateModel(
            name='StudentAnswer',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('answer_text', models.CharField(max_length=255)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CareerLink.question')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
