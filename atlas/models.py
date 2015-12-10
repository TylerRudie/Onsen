from django.db import models
from django.db.models import Sum, Q
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
    firstName = models.CharField('First Name',
                                max_length=100,
                                 )
    lastName  = models.CharField('Last Name',
                                max_length=100,
                                 )
    address1  = models.CharField('Address 1',
                                max_length=100,
                                 blank=True)
    address2  = models.CharField('Address 2',
                                max_length=100,
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

    default_seat_revenue = models.PositiveIntegerField('Default Seat Revenue',
                                                        blank=True,
                                                        null=True,)

    default_projector_revenue = models.PositiveIntegerField('Default Projector Revenue',
                                                            blank=True,
                                                            null=True,)

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

    available = models.BooleanField(default=True)

    seat = models.BooleanField(default=False)

    cost = models.PositiveIntegerField('Item Cost',
                                       blank=True,
                                       null=True)

    class Meta:
            verbose_name = 'Hardware'
            verbose_name_plural = 'Hardware'

    def __unicode__(self):
        return self.serialNum + ' [' +self.desc + ']'

    @property
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
            ## Because i do not believe the save will catch all of them, this is to catch what it fails
            if self.available is not True:
                self.available = True
                self.save()

            return 'Available'

    @property
    def total_revenue(self):

        if self.type == 'Laptop' or self.type == 'Workstation':
            rev = assignment.objects.filter(Q(
                                                hardwareID=self.hwID,
                                                outUser__isnull=False,
                                                inUser__isnull=True,
                                                eventID__end__lte= timezone.now())| Q(
                                                hardwareID=self.hwID,
                                                outUser__isnull=False,
                                                inUser__isnull=False,
                                                )
                                        ).aggregate(Sum('eventID__seat_revenue'))
            if rev['eventID__seat_revenue__sum'] is not None:
                return rev['eventID__seat_revenue__sum']

            else:
                return 0

        elif self.type == 'Projector':
            rev = assignment.objects.filter(Q(
                                                hardwareID=self.hwID,
                                                outUser__isnull=False,
                                                inUser__isnull=True,
                                                eventID__end__lte= timezone.now())| Q(
                                                hardwareID=self.hwID,
                                                outUser__isnull=False,
                                                inUser__isnull=False,
                                                )
                                        ).aggregate(Sum('eventID__projector_revenue'))
            if rev['eventID__projector_revenue__sum'] is not None:
                return rev['eventID__projector_revenue__sum']

            else:
                return 0
        else:
            return 0

    @property
    def last_event(self):
        le = self.events.latest(field_name='end')
        if le is None:
            return ""
        else:
            return le
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

    cfg_name =  models.CharField('Name',
                                blank=True,
                                max_length=200)

    days_Conf = models.IntegerField('Additional Days',
                                    blank=True,
                                    validators=[MinValueValidator(0)],
                                    null=True
                                    )
    not_load = models.BooleanField('Scheduling',
                                   default=False)

    def __unicode__(self):
        return self.cfg_name + '<' + self.days_Conf.__str__() +'>'
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

    seat_revenue = models.PositiveIntegerField('Seat Revenue',
                                                blank=True,
                                                null=True,)

    projector_revenue = models.PositiveIntegerField('Projector Revenue',
                                                    blank=True,
                                                    null=True,)

    Shipping_To = models.CharField('Airbills To Event',
                                    max_length=1000,
                                    blank=True,
                                    null=True,)

    Shipping_From = models.CharField('Airbills From Event',
                                    max_length=1000,
                                    blank=True,
                                    null=True,)

    def __unicode__(self):
        return self.title


    def Transition_to_event(self):
        if (self.prevEvent.count() > 0 ):
            return None
        elif (self.start):
            cfgDays = self.configAssigned.all().aggregate(Sum('days_Conf'))
            # print(cfgDays)
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

    ##TODO figure out how to deal with year boundary events

    @property
    def event_weeks(self):
        if self.start.isocalendar()[1] > self.end.isocalendar()[1]:
            return range(self.start.isocalendar()[1],54)
        else:
            return range(self.start.isocalendar()[1], self.end.isocalendar()[1]+1)


    @property
    def trans_to_weeks(self):
        if self.Transition_to_event is not None:
            if self.Transition_to_event().isocalendar()[1] > self.start.isocalendar()[1]:
                w = range(self.Transition_to_event().isocalendar()[1],54)
            else:
                w = range(self.Transition_to_event().isocalendar()[1],self.start.isocalendar()[1]+1)
            return [item for item in w if item not in self.event_weeks]
        else:
            return None

    @property
    def trans_from_weeks(self):
        if self.Transition_from_event is not None:
            if self.end.isocalendar()[1] > self.Transition_from_event().isocalendar()[1]:
                w = range(self.end.isocalendar()[1], 54)
            else:
                w = range(self.end.isocalendar()[1], self.Transition_from_event().isocalendar()[1]+1)
            return [item for item in w if item not in self.event_weeks]

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

    class Meta:
        unique_together = ('eventID', 'hardwareID',)

    def __unicode__(self):
        return self.eventID.title + '<>' + self.hardwareID.serialNum

    def save(self, *args, **kwargs):

        if self.outUser is not None and self.inUser is not None:
            self.hardwareID.available = True
        else:
            self.hardwareID.available = False

        self.hardwareID.save()
        super(assignment, self).save(*args, **kwargs)