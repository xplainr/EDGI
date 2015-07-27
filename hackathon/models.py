from django.db import models

class User(models.Model):
	username = models.CharField(max_length=255)
	access_token = models.TextField()
	is_admin = models.BooleanField(default=False)
	group_name = models.CharField(max_length=255,default="No Group")