# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Account(models.Model):
    """
    Extending the Django default User object.
    ref: https://docs.djangoproject.com/en/1.10/topics/auth/customizing/#extending-the-existing-user-model

        This adds an avatar field, in addition to providing
        some helper functions
    """

    # fb messenger info
    fb_user_psid        = models.CharField(max_length=1000, blank=True)
    fb_user_first_name  = models.CharField(max_length=1000, blank=True)
    fb_user_last_name   = models.CharField(max_length=1000, blank=True)
    fb_user_profile_pic = models.CharField(max_length=1000, blank=True)
    fb_user_locale      = models.CharField(max_length=1000, blank=True)
    fb_user_gender      = models.CharField(max_length=1000, blank=True)
    fb_user_timezone    = models.CharField(max_length=1000, blank=True)
    
    time_created        = models.DateTimeField(auto_now_add=True)
    time_modified       = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '{0}'.format(self.fb_user_psid)
