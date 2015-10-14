from django.shortcuts import render
from django.http import HttpResponse
from fullcalendar.util import events_to_json, calendar_options
import models

OPTIONS = """{  timeFormat: "H:mm",
                header: {
                    left: 'prev,next today',
                    center: 'title',
                    right: 'month,basicWeek,basicDay',
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

def calandar(request):
    event_url = 'all_events/'
    return render(request, 'calandar.html', {'calendar_config_options': calendar_options(event_url, OPTIONS)})
# Create your views here.

def home(request):
    return render(request, "home.html", {})


def all_events(request):
    events = models.event.objects.all()
    return HttpResponse(events_to_json(events), content_type='application/json')