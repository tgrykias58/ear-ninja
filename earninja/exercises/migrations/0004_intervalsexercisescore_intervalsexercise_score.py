# Generated by Django 4.2.11 on 2024-03-25 21:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('exercises', '0003_alter_interval_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='IntervalsExerciseScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_correct_answers', models.IntegerField(default=0)),
                ('num_all_answers', models.IntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='intervalsexercise',
            name='score',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='exercise', to='exercises.intervalsexercisescore'),
        ),
    ]