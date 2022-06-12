# Generated by Django 4.0.4 on 2022-06-04 13:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Crawler',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('consumer_key', models.CharField(default=None, help_text='Consumer key of twitter API', max_length=255)),
                ('consumer_secret', models.CharField(default=None, help_text='Consumer secret of twitter API', max_length=255)),
                ('access_token', models.CharField(default=None, help_text='Access key of twitter API', max_length=255)),
                ('access_secret', models.CharField(default=None, help_text='Consumer secret of twitter API', max_length=255)),
                ('bearer_token', models.CharField(default=None, help_text='Bearer key of twitter API', max_length=255)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='crawler', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StreamData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_running', models.IntegerField(default=0, help_text='Specifies if the stream is running')),
                ('query', models.CharField(blank=True, default='', help_text='List of comma-separated keywords to filter the stream', max_length=255)),
                ('duration', models.DurationField(help_text='Stream will run for the specified duration')),
                ('elapsed', models.DurationField(help_text='Elapsed duration of the stream')),
                ('crawler', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='stream_data', to='crawler.crawler')),
            ],
        ),
    ]
