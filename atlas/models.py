from django.db import models
from django.db.models import Sum
from django.conf import settings
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
from django.core.validators import MinValueValidator
from exclusivebooleanfield.fields import ExclusiveBooleanField
import atlas.util
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

    contact = models.ForeignKey(contact,
                                blank=True,
                                null=True)

    cost_center = models.IntegerField(blank=True,
                                    validators=[MinValueValidator(0)],
                                    null=True
                                    )
    retired = models.BooleanField(default=False)

    default = ExclusiveBooleanField()

    def __unicode__(self):
        return  self.poolName
###############################################

class hardware(models.Model):

    hwID      = models.UUIDField(primary_key=True,
                                 default=uuid.uuid4,
                                 editable=False)

    serialNum = models.CharField('Serial Number',
                                 max_length=100)

    desc      = models.CharField('Description',
                                 max_length=100,
                                 blank=True)

    config    = models.CharField('Configuration',
                                 max_length=100,
                                 blank=True)

    type      = models.CharField(max_length=100,
                                 blank=True,
                                 choices=settings.HARDWARE_TYPES)

    poolID    = models.ForeignKey(pool)

    class Meta:
            verbose_name = 'Hardware'
            verbose_name_plural = 'Hardware'

    def __unicode__(self):
        return self.serialNum

    def status(self):

        if self.poolID.retired:
            return 'Retired'

        elif (assignment.objects.filter(hardwareID=self.hwID,
                                        eventID__limbo=True,
                                        inUser__isnull=True
                                        ).count() > 0):
            return 'Limbo'

        elif (assignment.objects.filter(hardwareID=self.hwID,
                                        outUser__isnull=True,
                                        inUser__isnull=True
                                        ).count() > 0):
            return 'Setup'

        elif (assignment.objects.filter(hardwareID=self.hwID,
                                        outUser__isnull=False,
                                        inUser__isnull=True,
                                        eventID__start__gt= timezone.now()
                                        ).count() > 0):
            return 'Transfer To'

        elif (assignment.objects.filter(hardwareID=self.hwID,
                                        outUser__isnull=False,
                                        inUser__isnull=True,
                                        eventID__start__lte= timezone.now(),
                                        eventID__end__gt= timezone.now()
                                        ).count() > 0):
            return 'At Event'

        elif (assignment.objects.filter(hardwareID=self.hwID,
                                        outUser__isnull=False,
                                        inUser__isnull=True,
                                        eventID__end__lte= timezone.now()
                                        ).count() > 0):
            return 'Transfer From'

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

    lastStatus = models.CharField(max_length=100,
                                   blank=True)

    used       = models.BooleanField(default=False)

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
    not_load = models.BooleanField(default=False)

    def __unicode__(self):
        return self.cfg_name
###############################################


class event(models.Model):

    evID    =  models.UUIDField(primary_key=True,
                             default=uuid.uuid4,
                             editable=False)

    title   = models.CharField('Title',
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


    hwAssigned = models.ManyToManyField(hardware,
                                        blank=True,
                                        through='assignment',
                                        verbose_name='Assigned Hardware',
                                        related_name='events',
                                        )

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
                             verbose_name='Pool')

    limbo = models.BooleanField(default=False)

    def __unicode__(self):
        return self.title


    def Transition_to_event(self):
        if (self.prevEvent.count() > 0 ):
            return None
        elif (self.start):
            cfgDays = self.configAssigned.all().aggregate(Sum('days_Conf'))
            print(cfgDays)
            if cfgDays['days_Conf__sum'] is None:
                totalDays = settings.TRANS_DAYS

            else:
                totalDays = cfgDays['days_Conf__sum'] + settings.TRANS_DAYS


            return atlas.util.sub_business_days(self.start, totalDays)
        else:
            return None


    Transition_to_event.short_description = 'Transition to Event'

    def Transition_from_event(self):
        if (self.nextEvent):
            return None
        elif (self.end):
            return atlas.util.add_business_days(self.end, settings.TRANS_DAYS)
        else:
            return None


    Transition_from_event.short_description = 'Transition from Event'


## TODO setup with reverse URL lookup
    @property
    def url(self):
        return '/events/edit/' + str(self.evID) + '/'

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