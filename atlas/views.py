from django.shortcuts import render, render_to_response, get_object_or_404
from django.http import HttpResponse
from fullcalendar.util import events_to_json, calendar_options
from .forms import eventForm
from .models import event
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

def calendar(request):
    event_url = 'all_events/'
    return render(request, 'events/calendar.html', {'calendar_config_options': calendar_options(event_url, OPTIONS)})
# Create your views here.


def home(request):
    return render(request, "home.html", {})


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

def all_events(request):
    events = event.objects.all()
    return HttpResponse(events_to_json(events), content_type='application/json')