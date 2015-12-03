# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-03 07:08
from __future__ import unicode_literals

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
            name='AccessLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accessed_on', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uri', models.CharField(max_length=100)),
                ('title', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Revision',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('doc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spaces.Document')),
            ],
        ),
        migrations.CreateModel(
            name='Space',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('uri', models.CharField(max_length=100, verbose_name=b'URI')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='document',
            name='latest',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spaces.Revision'),
        ),
        migrations.AddField(
            model_name='document',
            name='space',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spaces.Space'),
        ),
        migrations.AddField(
            model_name='comment',
            name='document',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spaces.Document'),
        ),
        migrations.AddField(
            model_name='comment',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spaces.Comment'),
        ),
        migrations.AddField(
            model_name='accesslog',
            name='document',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spaces.Document'),
        ),
        migrations.AddField(
            model_name='accesslog',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]