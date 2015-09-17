from django.db import models
import uuid
# Create your models here.

class event(models.Model):
    evid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)



class hardware(models.Model):
    hwid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)