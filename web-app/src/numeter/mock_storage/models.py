from django.db import models

class Host(models.Model):
	ID = models.CharField(max_length=300, db_column="hostid")
