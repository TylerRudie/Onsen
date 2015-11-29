# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.validators
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='airbill',
            fields=[
                ('abID', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('tracking', models.CharField(max_length=100)),
                ('lastStatus', models.CharField(max_length=100, blank=True)),
                ('used', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='assignment',
            fields=[
                ('asgID', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('outTimeStamp', models.DateTimeField(null=True, verbose_name=b'Outbound Timestamp', blank=True)),
                ('inTimeStamp', models.DateTimeField(null=True, verbose_name=b'Inbound Timestamp', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='case',
            fields=[
                ('caseID', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('caseName', models.CharField(max_length=200, verbose_name=b'Case ID', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='configuration',
            fields=[
                ('cfgID', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('cfg_name', models.CharField(max_length=200, verbose_name=b'Title', blank=True)),
                ('days_Conf', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
            ],
        ),
        migrations.CreateModel(
            name='contact',
            fields=[
                ('ctID', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('firstName', models.CharField(max_length=100, blank=True)),
                ('lastName', models.CharField(max_length=100, blank=True)),
                ('address1', models.CharField(max_length=100, blank=True)),
                ('address2', models.CharField(max_length=100, blank=True)),
                ('city', models.CharField(max_length=100, blank=True)),
                ('state', models.CharField(max_length=100, blank=True)),
                ('zip', models.CharField(max_length=100, blank=True)),
                ('phone', models.CharField(max_length=100, blank=True)),
                ('email', models.EmailField(max_length=254, blank=True)),
                ('company', models.CharField(max_length=100, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='event',
            fields=[
                ('evID', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('title', models.CharField(max_length=200, verbose_name=b'Title', blank=True)),
                ('start', models.DateTimeField(verbose_name=b'Start')),
                ('end', models.DateTimeField(verbose_name=b'End')),
                ('all_day', models.BooleanField(default=False, verbose_name=b'All day')),
                ('laptopsRequested', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('projectorRequested', models.BooleanField(default=False)),
                ('dateShipped', models.DateField(null=True, verbose_name=b'Date Shipped', blank=True)),
                ('status', models.BooleanField(default=True)),
                ('site', models.CharField(max_length=200, blank=True)),
            ],
            options={
                'verbose_name': 'Event',
                'verbose_name_plural': 'Events',
            },
        ),
        migrations.CreateModel(
            name='event_airbill',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('toEvent', models.BooleanField(default=False)),
                ('evID', models.ForeignKey(to='atlas.event')),
                ('tracking', models.ForeignKey(to='atlas.airbill')),
            ],
        ),
        migrations.CreateModel(
            name='hardware',
            fields=[
                ('hwID', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('serialNum', models.CharField(max_length=100)),
                ('desc', models.CharField(max_length=100, blank=True)),
                ('config', models.CharField(max_length=100, blank=True)),
                ('type', models.CharField(max_length=100, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='pool',
            fields=[
                ('poolID', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('poolName', models.CharField(max_length=200, verbose_name=b'Pool Name', blank=True)),
                ('cost_center', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('contact', models.ForeignKey(to='atlas.contact')),
            ],
        ),
        migrations.AddField(
            model_name='hardware',
            name='poolID',
            field=models.ForeignKey(blank=True, to='atlas.pool', null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='abAssigned',
            field=models.ManyToManyField(to='atlas.airbill', verbose_name=b'Assigned Airbills', through='atlas.event_airbill', blank=True),
        ),
        migrations.AddField(
            model_name='event',
            name='caseAssigned',
            field=models.ManyToManyField(to='atlas.case', blank=True),
        ),
        migrations.AddField(
            model_name='event',
            name='configAssigned',
            field=models.ManyToManyField(to='atlas.configuration', blank=True),
        ),
        migrations.AddField(
            model_name='event',
            name='hwAssigned',
            field=models.ManyToManyField(related_name='events', verbose_name=b'Assigned Hardware', to='atlas.hardware', through='atlas.assignment', blank=True),
        ),
        migrations.AddField(
            model_name='event',
            name='instructor_contact',
            field=models.ManyToManyField(related_name='instCnt', to='atlas.contact', blank=True),
        ),
        migrations.AddField(
            model_name='event',
            name='nextEvent',
            field=models.ForeignKey(related_name='prevEvent', verbose_name=b'Next Event', blank=True, to='atlas.event', null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='pool',
            field=models.ForeignKey(verbose_name=b'Pool', blank=True, to='atlas.pool', null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='shipping_contact',
            field=models.ForeignKey(related_name='shippingCnt', blank=True, to='atlas.contact', null=True),
        ),
        migrations.AddField(
            model_name='assignment',
            name='eventID',
            field=models.ForeignKey(to='atlas.event'),
        ),
        migrations.AddField(
            model_name='assignment',
            name='hardwareID',
            field=models.ForeignKey(to='atlas.hardware'),
        ),
        migrations.AddField(
            model_name='assignment',
            name='inUser',
            field=models.ForeignKey(related_name='checkin_user', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='assignment',
            name='outUser',
            field=models.ForeignKey(related_name='checkout_user', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
