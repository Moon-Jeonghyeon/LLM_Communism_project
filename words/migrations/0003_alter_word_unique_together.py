# Generated by Django 5.1 on 2024-08-26 03:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("words", "0002_topic_alter_word_word_alter_word_topic"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="word",
            unique_together={("word", "topic")},
        ),
    ]
