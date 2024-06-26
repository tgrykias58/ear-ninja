# Generated by Django 4.2.11 on 2024-03-25 18:29

from django.db import migrations, models
import django.db.models.deletion
import exercises.audio_file_path_manager


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Interval',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_semitones', models.IntegerField()),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='IntervalInstance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('audio', models.FileField(upload_to=exercises.audio_file_path_manager.AudioFilePathManager.get_interval_instance_audio_path)),
                ('start_note', models.IntegerField()),
                ('interval', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exercises.interval')),
            ],
        ),
    ]
