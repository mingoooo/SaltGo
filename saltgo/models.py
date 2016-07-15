# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


class Minion_Status(models.Model):
    minion_id = models.CharField(max_length=255)
    is_online = models.BooleanField()
    key_c = (
        ('A', 'Accepted'),
        ('D', 'Denied'),
        ('U', 'Unaccepted'),
        ('R', 'Rejected'),
    )
    key_status = models.CharField(max_length=10,
                                  choices=key_c)

    def __unicode__(self):
        return u'%s' % self.minion_id


class Jobs_History(models.Model):
    jid = models.CharField(max_length=255, primary_key=True)
    expr_from = models.CharField(max_length=10)
    target = models.TextField(max_length=50000)
    start_time = models.DateTimeField(auto_now=True)
    is_sls = models.BooleanField(default=False)
    sls = models.CharField(max_length=255, null=True)
    command = models.TextField(max_length=50000, null=True)
    user = models.ForeignKey(User)

    def __unicode__(self):
        return u'%s (%s)' % (self.jid, self.start_time)


class Jobs_Result(models.Model):
    jid = models.ForeignKey(Jobs_History)
    succeed = models.CharField(max_length=255)
    failed = models.CharField(max_length=255)
    result = models.TextField(max_length=50000, null=True)
    end_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s (%s)' % (self.jid, self.end_time)
