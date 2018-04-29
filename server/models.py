# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Token(models.Model):
  name = models.CharField(max_length=50)
  token = models.CharField(max_length=350)
  
  def __str__(self):
    return self.token
  def __getitem__(self, key):
    return self.name


class ServerTask(models.Model):
  guid = models.CharField(max_length=50)
  processed = models.IntegerField()