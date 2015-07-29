# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hackathon', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='group_name',
            field=models.CharField(default=b'No Group', max_length=255),
        ),
    ]
