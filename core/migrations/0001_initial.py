# Generated by Django 4.0.4 on 2022-06-26 11:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GeoPlaces',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('place', models.CharField(default=None, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(default=None, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Trend',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='lorem ipsum', max_length=255)),
                ('slug', models.SlugField(blank=True, max_length=255)),
                ('volume', models.PositiveIntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('as_of', models.DateTimeField(auto_now_add=True)),
                ('is_user_trend', models.IntegerField(default=0)),
                ('is_active', models.IntegerField(default=1)),
                ('geoplaces', models.ManyToManyField(blank=True, related_name='trend', to='core.geoplaces')),
                ('locations', models.ManyToManyField(blank=True, related_name='trend', to='core.location')),
                ('topics', models.ManyToManyField(blank=True, related_name='trend', to='core.topic')),
            ],
        ),
        migrations.CreateModel(
            name='Tweet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=280)),
                ('tid', models.BigIntegerField(blank=True, null=True)),
                ('like_count', models.BigIntegerField(blank=True, null=True)),
                ('retweet_count', models.BigIntegerField(blank=True, null=True)),
                ('reply_count', models.BigIntegerField(blank=True, null=True)),
                ('source', models.CharField(blank=True, max_length=255)),
                ('user_followers', models.IntegerField(blank=True, null=True)),
                ('user_name', models.CharField(blank=True, max_length=255)),
                ('user_id', models.BigIntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TrendStats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('like_count', models.IntegerField(null=True)),
                ('reply_count', models.IntegerField(null=True)),
                ('retweet_count', models.IntegerField(null=True)),
                ('min_followers', models.IntegerField(null=True)),
                ('max_followers', models.IntegerField(null=True)),
                ('average_followers', models.IntegerField(null=True)),
                ('calculated_upto', models.BigIntegerField(blank=True, null=True)),
                ('trend', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.trend')),
            ],
        ),
        migrations.CreateModel(
            name='TrendSources',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source_name', models.CharField(max_length=255, null=True)),
                ('count', models.IntegerField(null=True)),
                ('trend_stats', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='trend_sources', to='core.trendstats')),
            ],
        ),
        migrations.CreateModel(
            name='TrendSentiment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pos_pol_count', models.IntegerField(null=True)),
                ('neg_pol_count', models.IntegerField(null=True)),
                ('neu_pol_count', models.IntegerField(null=True)),
                ('sub_count', models.IntegerField(null=True)),
                ('obj_count', models.IntegerField(null=True)),
                ('calculated_upto', models.BigIntegerField(blank=True, db_index=True, null=True)),
                ('top_pos_1', models.BigIntegerField(blank=True, null=True)),
                ('top_pos_2', models.BigIntegerField(blank=True, null=True)),
                ('top_pos_3', models.BigIntegerField(blank=True, null=True)),
                ('top_neg_1', models.BigIntegerField(blank=True, null=True)),
                ('top_neg_2', models.BigIntegerField(blank=True, null=True)),
                ('top_neg_3', models.BigIntegerField(blank=True, null=True)),
                ('top_neu_1', models.BigIntegerField(blank=True, null=True)),
                ('top_neu_2', models.BigIntegerField(blank=True, null=True)),
                ('top_neu_3', models.BigIntegerField(blank=True, null=True)),
                ('trend', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.trend')),
            ],
        ),
        migrations.AddField(
            model_name='trend',
            name='tweets',
            field=models.ManyToManyField(blank=True, db_index=True, related_name='trend', to='core.tweet'),
        ),
    ]
