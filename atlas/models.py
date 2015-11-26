from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
from django.core.validators import MinValueValidator
import uuid

###############################################
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
###############################################

class pool(models.Model):

    poolID   = models.UUIDField(primary_key=True,
                                default=uuid.uuid4,
                                editable=False)

    poolName = models.CharField('Pool Name',
                                blank=True,
                                max_length=200)

    contact = models.ForeignKey(contact)

    cost_center = models.IntegerField(blank=True,
                                    validators=[MinValueValidator(0)],
                                    null=True
                                    )
    def __unicode__(self):
        return  self.poolName
###############################################

class hardware(models.Model):

    hwID      = models.UUIDField(primary_key=True,
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

    def status(self):

        if (assignment.objects.filter(hardwareID=self.hwID,
                                      outUser__isnull=True).count() > 0):
            return 'Setup'
        elif (assignment.objects.filter(hardwareID=self.hwID,
                                        outUser__isnull=False,
                                        eventID__start__gt= timezone.now() ).count() > 0):
            return 'TransferTo'

        elif (assignment.objects.filter(hardwareID=self.hwID,
                                        outUser__isnull=False,
                                        eventID__start__lte= timezone.now(),
                                        eventID__end__gt= timezone.now() ).count() > 0):
            return 'AtEvent'

        elif (assignment.objects.filter(hardwareID=self.hwID,
                                        outUser__isnull=False,
                                        eventID__end__lte= timezone.now() ).count() > 0):
            return 'TransferFrom'

        elif (assignment.objects.filter(hardwareID=self.hwID,
                                        outUser__isnull=False,
                                        eventID__end__lte= timezone.now() ).count() > 0):
            return 'TransferFrom'

        else:
            return 'Available'
###############################################

class case(models.Model):
    caseID = models.UUIDField(primary_key=True,
                              default=uuid.uuid4,
                              editable=False)

    caseName = models.CharField('Case ID',
                                blank=True,
                                max_length=200)
    def __unicode__(self):
        return self.caseName
###############################################

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
###############################################

class configuration (models.Model):
    cfgID =     models.UUIDField(primary_key=True,
                                default=uuid.uuid4,
                                editable=False)

    cfg_name =  models.CharField('Title',
                                blank=True,
                                max_length=200)

    days_Conf = models.IntegerField(blank=True,
                                    validators=[MinValueValidator(0)],
                                    null=True
                                    )
    def __unicode__(self):
        return self.cfg_name
###############################################

class event(models.Model):

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
                                            validators=[MinValueValidator(0)],
                                            null=True)

    projectorRequested = models.BooleanField(default=False)

    dateShipped = models.DateField('Date Shipped',
                                   blank=True,
                                   null=True)

    status = models.BooleanField(default=True)

    hwAssigned = models.ManyToManyField(hardware,
                                        blank=True,
                                        through='assignment',
                                        verbose_name='Assigned Hardware',
                                        related_name='events')

    shipping_contact = models.ForeignKey(contact,
                                         blank = True,
                                         null = True,
                                         related_name='shippingCnt'
                                        )

    instructor_contact = models.ManyToManyField(contact,
                                                blank = True,
                                                related_name='instCnt'
                                                )

    abAssigned = models.ManyToManyField(airbill,
                                        through='event_airbill',
                                        blank=True,
                                        verbose_name='Assigned Airbills')

    caseAssigned = models.ManyToManyField(case,
                                          blank=True)

    configAssigned = models.ManyToManyField(configuration,
                                            blank=True)

    site = models.CharField(max_length=200,
                            blank=True)

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


    def Transition_to_event(self):
        if (self.prevEvent.count() > 0 ):
            return None
        elif (self.start):
            return self.start - timedelta(days=settings.TRANS_DAYS)
        else:
            return None
        Tran_to_event.verbose = ''


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

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'



###############################################

class event_airbill(models.Model):

    evID = models.ForeignKey(event)
    tracking = models.ForeignKey(airbill)
    toEvent  = models.BooleanField(default=False)

    def __unicode__(self):
        return self.tracking.tracking + ' <> ' + self.evId.name

    class meta:
        verbose_name = 'Assigned Airbill'


class assignment(models.Model):

    asgID = models.UUIDField(primary_key=True,
                                default=uuid.uuid4,
                                editable=False)

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