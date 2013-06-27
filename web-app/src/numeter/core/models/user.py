from django.db import models


class User(models.Model):
	nickname = models.CharField(max_length=200)
	email = models.CharField(max_length=200)
	password = models.CharField(max_length=200)


class Group(models.Model):
	models.ForeignKey(User)
	models.ForeignKey('Host')
