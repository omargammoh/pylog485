from django.db import models

class Reading(models.Model):
    data = models.TextField()
    meta = models.TextField()

class Conf(models.Model):
    data = models.TextField()
    meta = models.TextField()

class Monitor(models.Model):
    data = models.TextField()
    meta = models.TextField()

