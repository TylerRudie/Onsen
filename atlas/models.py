from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from datetime import timedelta
import uuid


class contact(models.Model):
    ctID      = models.UUIDField(primary_key=True,
                                 default=uuid.uuid4,
                                 editable=False)
    firstName = models.CharField(max_length=100,
                                 blank=True)
    lastName  = models.CharField(max_length=100,
                                 blank=True)
    address1  = models.CharField(max_length=100,
                                 blank=True)
    address2  = models.CharField(max_length=100,
                                 blank=True)
    city      = models.CharField(max_length=100,
                                 blank=True)
    state     = models.CharField(max_length=100,
                                 blank=True)
    zip       = models.CharField(max_length=100,
                                 blank=True)
    phone     = models.CharField(max_length=100,
                                 blank=True)
    email     = models.EmailField(blank=True)
    company   = models.CharField(max_length=100,
                                 blank=True)

    def __unicode__(self):
        return self.firstName + ' ' + self.lastName + ' <' + self.email + '>'

class pool(models.Model):

    poolID   = models.UUIDField(primary_key=True,
                                default=uuid.uuid4,
                                editable=False)

    poolName = models.CharField('Pool Name',
                                blank=True,
                                max_length=200)

    Contact = models.ForeignKey(contact)

    def __unicode__(self):
        return  self.poolName


class hardware(models.Model):
    # status_choices = (
    #     ('a','Active'),
    #     ('s','Standby'),
    #     ('i','Inactive'),
    # )
    hwId      = models.UUIDField(primary_key=True,
                                 default=uuid.uuid4,
                                 editable=False)

    serialNum = models.CharField(max_length=100)

    desc      = models.CharField(max_length=100,
                                 blank=True)

    config    = models.CharField(max_length=100,
                                 blank=True)

    type      = models.CharField(max_length=100,
                                 blank=True)

    poolID    = models.ForeignKey(pool, blank=True,
                                  null=True)

    def __unicode__(self):
        return self.serialNum


class case(models.Model):
    caseID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    caseName = models.CharField('Case ID', blank=True, max_length=200)
    def __unicode__(self):
        return self.caseName


class airbill(models.Model):

    abID      = models.UUIDField(primary_key=True,
                                default=uuid.uuid4,
                                editable=False)

    tracking   = models.CharField(max_length=100,
                                  )

    lastStatus = models.CharField (max_length=100,
                                   blank=True)

    used       = models.BooleanField (default=False)

    def __unicode__(self):
        return self.tracking


class event(models.Model):
    status_choices = (
        ('e','Event'),
        ('i','Inactive'),
        # ('p','Pool'),
    )

    evID    =  models.UUIDField(primary_key=True,
                             default=uuid.uuid4,
                             editable=False)

    title   = models.CharField('Title',
                             blank=True,
                             max_length=200)

    start   = models.DateTimeField('Start')

    end     = models.DateTimeField('End')

    all_day = models.BooleanField('All day',
                                  default=False)

    laptopsRequested = models.IntegerField(blank=True,
                                           null=True)

    projectorRequested = models.BooleanField(default=False)

    dateShipped = models.DateField('Date Shipped',
                                   blank=True,
                                   null=True)

    status = models.CharField(max_length=100,
                              choices=status_choices,
                              default='Event')

    hwAssigned = models.ManyToManyField(hardware,
                                        blank=True,
                                        through='assignment',
                                        verbose_name='Assigned Hardware',
                                        related_name='events')

    ctAssigned = models.ManyToManyField(contact,
                                        through='contact_event',
                                        blank=True,
                                        verbose_name='Assigned Contacts')

    abAssigned = models.ManyToManyField(airbill,
                                        through='event_airbill',
                                        blank=True,
                                        verbose_name='Assigned Airbills')

    caseAssigned = models.ManyToManyField(case, blank=True)

    site = models.CharField(max_length=200, blank=True)

    nextEvent = models.ForeignKey("self",
                                  blank=True,
                                  null=True,
                                  verbose_name='Next Event',
                                  related_name='prevEvent')

    pool = models.ForeignKey(pool,
                             blank=True,
                             null=True,
                             verbose_name='Pool')





    def __unicode__(self):
        return self.title


    # def _getStartWeek(self):
    #     return self.startDate.isocalendar()[1]

    def Transition_To_Event(self):
        if (self.prevEvent.count() > 0 ):
            return None
        elif (self.start):
            return self.start - timedelta(days=settings.TRANS_DAYS)
        else:
            return None
        Tran_To_Event.verbose = ''

    def Transition_from_event(self):
        if (self.nextEvent):
            return None
        elif (self.end):
            return self.end + timedelta(days=settings.TRANS_DAYS)
        else:
            return None
    Transition_from_event.short_description = 'Transition from Event'

    @property
    def url(self):

        return '/events/edit/' +  str(self.evID) + '/'


    # TranToEvent = property(_getTranToEvent)
    # TranFromEvent = property(_getTranFromEvent)
    #
    # startWeek = property(_getStartWeek)

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'


class contact_event(models.Model):

    ctID       = models.ForeignKey(contact)
    evID       = models.ForeignKey(event)
    isShipping = models.BooleanField(default=False)
    isInst     = models.BooleanField(default=False)

    def __unicode__(self):
        return self.ctID.firstName + ' ' + self.ctID.lastName + '<>' + self.evID.title

    class meta:
        verbose_name = 'Assigned Contacts'


class event_airbill(models.Model):

    evID = models.ForeignKey(event)
    tracking = models.ForeignKey(airbill)
    toEvent  = models.BooleanField(default=False)

    def __unicode__(self):
        return self.tracking.tracking + ' <> ' + self.evId.name

    class meta:
        verbose_name = 'Assigned Airbill'


class assignment(models.Model):
    eventID = models.ForeignKey(event)
    hardwareID = models.ForeignKey(hardware)
    outTimeStamp = models.DateTimeField('Outbound Timestamp',
                                        blank=True,
                                        null=True)
    outUser = models.ForeignKey(User, blank=True,
                                related_name='checkout_user',
                                null=True)
    inTimeStamp = models.DateTimeField('Inbound Timestamp',
                                       blank=True,
                                       null=True)
    inUser = models.ForeignKey(User, blank=True,
                               related_name='checkin_user',
                               null=True)

    def __unicode__(self):
        return self.eventID.title + '<>' + self.hardwareID.serialNum