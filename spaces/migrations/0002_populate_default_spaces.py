# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-08 04:39
from __future__ import unicode_literals

from django.db import migrations


def create_root_space(apps, schema_editor):
    """ Create a default ROOT space """
    Space = apps.get_model("spaces", "Space")
    Space.objects.create(id=1, name="__ROOT__", path="")
    Space.objects.create(id=2, name="__USER__", path="user")


def rollback_space(apps, schema_editor):
    """ Remove default spaces """
    Space = apps.get_model("spaces", "Space")
    try:
        Space.objects.get(path="").delete()
    except:
        pass
    try:
        Space.objects.get(path="user").delete()
    except:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('spaces', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_root_space, rollback_space),
    ]