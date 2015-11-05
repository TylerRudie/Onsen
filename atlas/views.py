from django.shortcuts import render, render_to_response, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from fullcalendar.util import events_to_json, calendar_options
from .forms import eventForm, hardwareForm, contactForm, airbillForm, poolForm
from .models import event, hardware, contact, airbill, pool
from django.views.generic.list import ListView
from django.utils import timezone
from django.utils.decorators import method_decorator

## TODO - Update window.open to use URL reverse introspection (Do not hard code)
OPTIONS = """{  timeFormat: "H:mm",
                    customButtons: {
                        NewEvent: {
                            text: 'New',
                            click: function() {
                                window.open('/events/new/');
                                return false;
                            }
                        }
                    },
                header: {
                    left: 'prev,next today NewEvent',
                    center: 'title',
                    right: 'month, basicWeek, basicDay',
                },
                allDaySlot: true,
                firstDay: 0,
                weekMode: 'liquid',
                slotMinutes: 15,
                defaultEventMinutes: 30,
                minTime: 8,
                maxTime: 20,
                editable: false,
                weekNumbers: true,
                weekNumberTitle: "Week",

                dayClick: function(date, allDay, jsEvent, view) {
                    if (allDay) {
                        $('#calendar').fullCalendar('gotoDate', date)
                        $('#calendar').fullCalendar('changeView', 'basicDay')
                    }
                },
                eventClick: function(event, jsEvent, view) {
                    if (view.name == 'month') {
                        $('#calendar').fullCalendar('gotoDate', event.start)
                        $('#calendar').fullCalendar('changeView', 'basicDay')
                    }
                },
            }"""

@login_required
def home(request):
    return render(request, "home.html", {})


@login_required
def calendar(request):
    event_url = 'all_events/'
    return render(request, 'events/calendar.html', {'calendar_config_options': calendar_options(event_url, OPTIONS)})
# Create your views here.


@login_required
def all_events(request):
    events = event.objects.all()
    return HttpResponse(events_to_json(events), content_type='application/json')


##TODO add ability to delete events

@login_required
def new_event(request):
    title = 'New Event'
    form = eventForm(request.POST or None)

    if request.POST:
            form = eventForm(request.POST)
            if form.is_valid():
                form.save()

    context = {
        "title": title,
        "form": form
    }

    return render(request, "events\event.html", context)


@login_required
def edit_event(request, uuid=None):
    title = 'Edit Event'
    if uuid:
        thisEvent = get_object_or_404(event, evID=uuid)
## TODO fix M2M save 'Cannot set values on a ManyToManyField which specifies an intermediary model.'
    ## http://stackoverflow.com/questions/387686/what-are-the-steps-to-make-a-modelform-work-with-a-manytomany-relationship-with
    if request.POST:
        form = eventForm(request.POST, instance=thisEvent)
        if form.is_valid():
            form.save()

    else:
        form = eventForm(instance=thisEvent)

    print thisEvent


    context = {
        "title": title,
        "form": form
    }

    return render(request, "events\event.html", context)

###############################

@login_required
def new_hardware(request):
    title = 'New Hardware'
    form = hardwareForm(request.POST or None)

    if request.POST:
            form = hardwareForm(request.POST)
            if form.is_valid():
                form.save()

    context = {
        "title": title,
        "form": form
    }

    return render(request, "hardware\hardware.html", context)


@login_required
def edit_hardware(request, uuid=None):
    title = 'Edit Hardware'
    if uuid:
        thisObj = get_object_or_404(hardware, hwId=uuid)

    if request.POST:
        form = hardwareForm(request.POST, instance=thisObj)
        if form.is_valid():
            form.save()

    else:
        form = hardwareForm(instance=thisObj)

    print thisObj


    context = {
        "title": title,
        "form": form
    }

    return render(request, "hardware\hardware.html", context)

# @login_required
class list_hardware(ListView):

    model = hardware
    template_name = 'hardware/hwIndex.html.html'
    context_object_name = 'objects'

    def get_queryset(self):
        objList = hardware.objects.all()
        return objList

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(list_hardware, self).dispatch(*args, **kwargs)

#############################

@login_required
def new_contact(request):
    title = 'New Contact'
    form = contactForm(request.POST or None)

    if request.POST:
            form = contactForm(request.POST)
            if form.is_valid():
                form.save()

    context = {
        "title": title,
        "form": form
    }

    return render(request, "contact\contact.html", context)


@login_required
def edit_contact(request, uuid=None):
    title = 'Edit Contact'
    if uuid:
        thisObj = get_object_or_404(contact, ctID=uuid)

    if request.POST:
        form = contactForm(request.POST, instance=thisObj)
        if form.is_valid():
            form.save()

    else:
        form = contactForm(instance=thisObj)

    print thisObj


    context = {
        "title": title,
        "form": form
    }

    return render(request, "contact\contact.html", context)

#############################

@login_required
def new_airbill(request):
    title = 'New Airbill'
    form = airbillForm(request.POST or None)

    if request.POST:
            form = airbillForm(request.POST)
            if form.is_valid():
                form.save()

    context = {
        "title": title,
        "form": form
    }

    return render(request, "airbill/airbill.html", context)


@login_required
def edit_airbill(request, uuid=None):
    title = 'Edit Airbill'
    if uuid:
        thisObj = get_object_or_404(airbill, abID=uuid)

    if request.POST:
        form = airbillForm(request.POST, instance=thisObj)
        if form.is_valid():
            form.save()

    else:
        form = airbillForm(instance=thisObj)

    print thisObj


    context = {
        "title": title,
        "form": form
    }

    return render(request, "airbill/airbill.html", context)

###########################

@login_required
def new_pool(request):
    title = 'New Pool'
    form = poolForm(request.POST or None)

    if request.POST:
            form = poolForm(request.POST)
            if form.is_valid():
                form.save()

    context = {
        "title": title,
        "form": form
    }

    return render(request, "airbill/airbill.html", context)


@login_required
def edit_pool(request, uuid=None):
    title = 'Edit Pool'
    if uuid:
        thisObj = get_object_or_404(pool, poolID=uuid)

    if request.POST:
        form = poolForm(request.POST, instance=thisObj)
        if form.is_valid():
            form.save()

    else:
        form = poolForm(instance=thisObj)

    print thisObj


    context = {
        "title": title,
        "form": form
    }

    return render(request, "airbill/airbill.html", context)

