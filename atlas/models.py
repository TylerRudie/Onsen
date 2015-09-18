from django.db import models
import uuid
# Create your models here.


class hardware(models.Model):
    status_choices = (
        ('a','Active'),
        ('s','Standby'),
        ('i','Inactive'),
    )
    hwId      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    serialNum = models.CharField(max_length=100)
    desc      = models.CharField(max_length=100)
    config    = models.CharField(max_length=100)
    status    = models.CharField(max_length=100, choices = status_choices, default='Active' )

    def __str__(self):
        return self.serialNum

class event(models.Model):
    status_choices = (
        ('e','Event'),
        ('i','Inactive'),
        ('p','Pool'),
    )

    evId       = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name       = models.CharField(max_length=100)
    status     = models.CharField(max_length=100, choices=status_choices, default='Event')
    startDate  = models.DateField(max_length=100)
    endDate    = models.DateField(max_length=100)
    hwAssigned = models.ManyToManyField(hardware)

    def __str__(self):
        return self.name




