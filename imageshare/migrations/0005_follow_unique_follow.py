# Generated by Django 5.1.1 on 2024-10-04 09:57

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imageshare', '0004_alter_follow_options_alter_like_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('created_by', 'following'), name='unique_follow'),
        ),
    ]
