from django.db import models
import uuid
import datetime



class hardware(models.Model):
    status_choices = (
        ('a','Active'),
        ('s','Standby'),
        ('i','Inactive'),
    )
    hwId      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    serialNum = models.CharField(max_length=100)
    desc      = models.CharField(max_length=100, blank=True)
    config    = models.CharField(max_length=100, blank=True)
    status    = models.CharField(max_length=100, choices = status_choices, default='Active' )



    def __str__(self):
        return self.serialNum


class contact(models.Model):
    ctId      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    firstName = models.CharField(max_length=100, blank=True)
    lastName  = models.CharField(max_length=100, blank=True)
    address1  = models.CharField(max_length=100, blank=True)
    address2  = models.CharField(max_length=100, blank=True)
    city      = models.CharField(max_length=100, blank=True)
    state     = models.CharField(max_length=100, blank=True)
    zip       = models.CharField(max_length=100, blank=True)
    phone     = models.CharField(max_length=100, blank=True)
    email     = models.EmailField(blank=True)
    company   = models.CharField(max_length=100, blank=True)
    def __str__(self):
        return self.firstName + ' ' + self.lastName + ' <' + self.email + '>'


class airbill(models.Model):
    tracking   = models.CharField(max_length=100, primary_key=True)
    lastStatus = models.CharField (max_length=100, blank=True)
    used       = models.BooleanField (default=False)

    def __str__(self):
        return self.tracking


class event(models.Model):
    status_choices = (
        ('e','Event'),
        ('i','Inactive'),
        ('p','Pool'),
    )

    evId       = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name       = models.CharField(max_length=100)
    status     = models.CharField(max_length=100, choices=status_choices, default='Event')
    startDate  = models.DateField(max_length=100, blank=True)
    endDate    = models.DateField(max_length=100, blank=True)

    hwAssigned = models.ManyToManyField(hardware, blank=True)
    ctAssigned = models.ManyToManyField(contact, through='contact_event', blank=True)
    abAssigned = models.ManyToManyField(airbill, through='event_airbill', blank=True)

    def __str__(self):
        return self.name


    @property
    def startWeek(self):
        return self.startDate.isocalendar()[1]


class contact_event(models.Model):

    ctId       = models.ForeignKey(contact)
    evId       = models.ForeignKey(event)
    isShipping = models.BooleanField(default=False)
    isInst     = models.BooleanField(default=False)

    def __str__(self):
        return self.ctId.firstName + ' ' + self.ctId.lastName + '<>' + self.evId.name

class event_airbill(models.Model):

    evId = models.ForeignKey(event)
    tracking = models.ForeignKey(airbill)
    toEvent  = models.BooleanField(default=False)

    def __str__(self):
        return self.tracking.tracking + ' <> ' + self.evId.name