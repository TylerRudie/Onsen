from __future__ import division
import json
from django.shortcuts import render, render_to_response, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponse
from fullcalendar.util import events_to_json, calendar_options
from django.views.generic.edit import FormMixin
from django.views.generic.list import ListView
from django.utils import timezone
from django.utils.decorators import method_decorator
from easy_pdf.views import PDFTemplateView
from django.core.urlresolvers import reverse
from django.db.models import Q
from .util import get_default_pool, get_hw_staus_stats
from django.db.models import Sum, Count
from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.contrib.humanize.templatetags.humanize import intcomma
from datetime import timedelta
import json, datetime, itertools
from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from .forms import eventForm, hardwareForm, contactForm, airbillForm, poolForm, multiHardwareForm, configForm
from .models import event, hardware, contact, airbill, pool, assignment, configuration



## TODO - Update window.open to use URL reverse introspection (Do not hard code), and remove new window
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
            }"""

def home_redirect(request):
    return redirect('/')

@login_required
@login_required
def get_geo(request):
    weekevents = event.objects.all().filter(Q(start__lte=datetime.date.today(), end__gte=datetime.date.today()) | Q(start__lte=datetime.date.today()+timedelta(days=7),start__gte=datetime.date.today()))
    contactids = weekevents.values('shipping_contact_id')
#   addresses = [{x.address1, x.city, x.state, x.zip} for x in contact.objects.all().filter(ctID__in=contactids)]
#    addresses = [{x.address1.encode('utf8'), x.city.encode('utf8'), x.state.encode('utf8'), x.zip.encode('utf8')} for x in contact.objects.all().filter(ctID__in=contactids)]
#    addresses = contact.objects.all().filter(ctID__in=contactids).values_list('address1','city','state','zip')
    addresses = contact.objects.all().filter(ctID__in=contactids).values_list('address1','city','state','zip')
    utfformatted = [[x.encode("utf8") for x in sets] for sets in addresses]
    formatted = str(utfformatted).replace("'","").replace("[[","'").replace("[","'").replace(", '","'").replace("]]","'").replace("]","'")
#    formatted = str(utfformatted).replace("'","").replace("[[","'").replace("[","'").replace("]]","'").replace("]","'")
#    formatted = str(addresses).replace("'","").replace("[set","").replace("([","'").replace("])","'").replace(", ",",'").replace("]]","'")
#    formatted = str(addresses).replace("'","").replace("[set","").replace("([","'").replace("])","'").replace(", set'",",'").replace("]","'").replace("''","'")
    return JsonResponse(formatted, safe=False )

@login_required
def home(request):

#Map
    weekevents = event.objects.all().filter(Q(start__lte=datetime.date.today(), end__gte=datetime.date.today()) | Q(start__lte=datetime.date.today()+timedelta(days=7),start__gte=datetime.date.today()))
    contactids = weekevents.values('shipping_contact_id')
#   addresses = [{x.address1, x.city, x.state, x.zip} for x in contact.objects.all().filter(ctID__in=contactids)]
    addresses = [{x.address1.encode('utf8'), x.city.encode('utf8'), x.state.encode('utf8'), x.zip.encode('utf8')} for x in contact.objects.all().filter(ctID__in=contactids)]
#    addresses = contact.objects.all().filter(ctID__in=contactids).values_list('address1','city','state','zip')
#    addresses = contact.objects.all().filter(ctID__in=contactids).values_list('address1','city','state','zip')
#    utfformatted = [[x.encode("utf8") for x in sets] for sets in addresses]
#    formatted = str(utfformatted).replace("'","").replace("[[","'").replace("[","'").replace(", '",",'").replace("]]","'").replace("]","'")
    formatted = str(addresses).replace("'","").replace("[set","").replace('([','"').replace('])','"').replace(", set",',"').replace("]",'"').replace('""','"')

#    formatted = addresses
#    Total Completed Assignment
    tca = assignment.objects.filter(Q(
                                                outUser__isnull=False,
                                                inUser__isnull=True,
                                                eventID__end__lte= timezone.now())| Q(
                                                outUser__isnull=False,
                                                inUser__isnull=False,
                                                )
                                        )
#    Total Revenue
    trdata = tca.aggregate(Sum('eventID__seat_revenue')).values()[0]
    print trdata
    if trdata is not None:
        dollars = round(float(trdata), 2)
    else:
        dollars = 0
    print dollars
    tr = "$%s%s" % (intcomma(int(dollars)), ("%0.2f" % dollars)[-3:])

#     Total Events
    te = tca.values('eventID_id').distinct().count()

#    Total Hardware Shipped
    thsdata = tca.exclude(hardwareID__isnull=True).count()

    ths = thsdata

#    Total Hardware
    retiredpools=pool.objects.all().filter(retired=1)  # Retired Pools
    allhw=hardware.objects.all()  # All Hardware
    allhwa=allhw.exclude(poolID_id=retiredpools)  # All Hardware Available (Not Retired)

    hwneedssetup=assignment.objects.filter(hardwareID=allhw,outUser__isnull=True,inUser__isnull=True).count()

    th = allhw.exclude(poolID_id=retiredpools).count()  # Count of All Hardware (Not Retired)

    tha = allhw.filter(available=1).exclude(poolID_id=retiredpools)  # All Hardware Available (Not Retired)
    ta= tha.count()  # Count of All Hardware Available (Not Retired)

    thun = allhw.filter(available=0).exclude(poolID_id=retiredpools)  # All Hardware Unavailable (Not Retired)
    tau= thun.count() # Count of All Hardware Unavailable (Not Retired)

    tap= round((float(ta)/float(th)*100), 2)
    taup= round((float(tau)/float(th)*100), 2)

    tla= tha.filter(type='Laptop').count()
    tlaptops =allhwa.filter(type='Laptop').count()

    tpa= tha.filter(type='Project').count()
    tprojects= allhwa.filter(type='Projector').count()

    tsma= tha.filter(type='SpaceMouse').count()
    tspacemouse= allhwa.filter(type='SpaceMouse').count()

    if tprojects > 0:
        tprojects_num =  int((tla/tlaptops)*100)
    else:
        tprojects_num = 0

    if tlaptops > 0 :
        total_lp = int((tla/tlaptops)*100)
    else:
        total_lp = 0
    if tspacemouse > 0:
        total_smp = int((tsma/tspacemouse)*100)
    else:
        total_smp = 0

    context = {
            "title": 'Home',
            "laptop_usage": get_hw_staus_stats(hwType='Laptop'),
            "projector_usage": get_hw_staus_stats(hwType='Test'),
            "total_hardware": th,
            "total_havail": ta,
            "total_availpercent": tap,
            "hw_need_setup": hwneedssetup,
            "total_revenue": tr,
            "total_events": te,
            "total_hardware_shipped": ths,
            "total_hutilized": taup,
            "total_laptops_avail": tla,
            "total_laptops": tlaptops,
            "total_lp": total_lp,
            "total_projectors_avail": tpa,
            "total_projectors": tprojects,
            "total_pp":  tprojects_num,
            "total_sm_avail": tsma,
            "total_sm": tspacemouse,
            "total_smp": total_smp,
            "geo_code": formatted
        }

    return render(request, "home.html", context)


def draw_graph(request, x="None"):
    retiredpools=pool.objects.all().filter(retired=1)
    hwtype = hardware.objects.filter(type=x).exclude(poolID_id=retiredpools)
    total = hwtype.count()
    free = hwtype.filter(available=1).count()
    percent = int((free/total)*100)

    graph_data = []

    avail_data = {}
    avail_data["value"] = percent
    avail_data["label"] =  x+" Available"
    graph_data.append(avail_data)

    unavail_data = {}
    unavail_data["value"] = 100-percent
    unavail_data["label"] =  x+" Unavailable"
    graph_data.append(unavail_data)

    return JsonResponse(graph_data,safe=False)


###############################################

@login_required
def dashboard(request):

    return render(request, "dashboard.html", {})

@login_required
def logout(request):
    return render(request, "registration/logout.html", {})

###############################################
@login_required
def calendar(request):
    event_url = 'all_events/'
    return render(request, 'events/cl.html', {'calendar_config_options': calendar_options(event_url, OPTIONS)})
# Create your views here.


@login_required
def all_events(request):
    events = event.objects.all()
    return HttpResponse(events_to_json(events), content_type='application/json')
##TODO add ability to delete events

##TODO error with new and edit event on mobile chrome - 'Uncaught TypeError: Cannot read property 'hasClass' of undefineda.toggleMenu @ app.min.js:1(anonymous function) @ app.min.js:1n.event.dispatch @ jquery.min.js:3r.handle @ jquery.min.js:3'
@login_required
def new_event(request):
    title = 'New Event'
    df = get_default_pool()
    if df is None:
        form = eventForm(request.POST or None)
    else:
        form = eventForm(request.POST or None, initial={'pool': df,
                                                        'seat_revenue': df.default_seat_revenue,
                                                        'projector_revenue': df.default_projector_revenue})
    form.fields['nextEvent'].queryset = event.objects.none()
    form.fields['hwAssigned'].queryset = hardware.objects.filter(available=True, poolID__retired=False)
    if request.POST:
        form = eventForm(request.POST)
        if request.POST.get("_cancel"):
            return redirect(reverse('calendar'))
        else:
            if form.is_valid():
                fm = form.save(commit=False)
                fm.save()

                for asg_post in form.cleaned_data.get('hwAssigned'):
                    hwd_asg = assignment(eventID=fm, hardwareID=asg_post)

                    hwd_asg.save()


                obj = form.instance

                if request.POST.get("_stay"):
                    return redirect(reverse('event_edit', kwargs={'uuid': obj.pk} ))

                else:
                    return HttpResponseRedirect(reverse('calendar'))

            else:
                context = {
                    "title": title,
                    "form": form
                }

                return render(request, "events/event.html", context)


    else:
        context = {
            "title": title,
            "form": form
        }

        return render(request, "events/event.html", context)


@login_required
def edit_event(request, uuid=None):
    title = 'Edit Event'
    if uuid:
        thisEvent = get_object_or_404(event, evID=uuid)

    if request.POST:
        if request.POST.get("_cancel"):
            return redirect(reverse('calendar'))
        else:
            form = eventForm(request.POST, instance=thisEvent)

            if form.is_valid():
                fm = form.save(commit=False)
                fm.save()
################################
                fmList = form.cleaned_data.get('hwAssigned').all()
                objList = thisEvent.hwAssigned.all()

                for asg_post in fmList:
                    if asg_post not in objList:
                        asg = assignment(eventID=fm, hardwareID=asg_post)
                        asg.save()

                for obj in objList:
                    if obj not in fmList:
                        asg_obj = assignment.objects.get(hardwareID=obj, eventID=thisEvent.evID )
                        asg_obj.delete()
                        obj.available = True
                        obj.save()
###############################
                fmList_c = form.cleaned_data.get('instructor_contact').all()
                objList_c = thisEvent.instructor_contact.all()

                # print objList_c
                # print fmList_c

                for asg_post in fmList_c:
                    if asg_post not in objList_c:
                        thisEvent.instructor_contact.add(asg_post)

                for obj in objList_c:
                    if obj not in fmList_c:
                        print(obj)
                        thisEvent.instructor_contact.remove(obj)
###############################
                fmList_d = form.cleaned_data.get('caseAssigned').all()
                objList_d = thisEvent.caseAssigned.all()

                # print objList_d
                # print fmList_d

                for asg_post in fmList_d:
                    if asg_post not in objList_d:
                        thisEvent.caseAssigned.add(asg_post)

                for obj in objList_d:
                    if obj not in fmList_d:
                        print(obj)
                        thisEvent.caseAssigned.remove(obj)
#############################
                fmList_F = form.cleaned_data.get('configAssigned').all()
                objList_F = thisEvent.configAssigned.all()

                # print objList_d
                # print fmList_d

                for asg_post in fmList_F:
                    if asg_post not in objList_F:
                        thisEvent.configAssigned.add(asg_post)

                for obj in objList_F:
                    if obj not in fmList_F:
                        print(obj)
                        thisEvent.configAssigned.remove(obj)
#############################






                if request.POST.get("_stay"):
                    form = eventForm(instance=thisEvent)
                    form.fields['nextEvent'].queryset = event.objects.filter(start__gte= thisEvent.end)
                    form.fields['hwAssigned'].queryset = hardware.objects.filter(Q(available=True, poolID__retired=False) | Q(events__evID=thisEvent.evID))
                    print(thisEvent.hwAssigned.all())
                    context = {
                        "title": title,
                        "form": form,
                        "evID": thisEvent.evID
                    }
                    return render(request, "events/event.html", context)

                elif request.POST.get("_event_checkout"):
                    return redirect(reverse('event_checkout', kwargs={'uuid': thisEvent.pk} ))
                elif request.POST.get("_event_checkin"):
                    return redirect(reverse('event_checkin', kwargs={'uuid': thisEvent.pk} ))
                elif request.POST.get("_event_srf_pdf"):
                    return redirect(reverse('event_srf_pdf', kwargs={'uuid': thisEvent.pk} ))
                elif request.POST.get("_event_packing_pdf"):
                    return redirect(reverse('event_packing_pdf', kwargs={'uuid': thisEvent.pk} ))

                else:
                    return HttpResponseRedirect(reverse('calendar'))
            else:
                form = eventForm(instance=thisEvent)
                form.fields['nextEvent'].queryset = event.objects.filter(start__gte= thisEvent.end)
                form.fields['hwAssigned'].queryset = hardware.objects.filter(Q(available=True, poolID__retired=False) | Q(events__evID=thisEvent.evID))
                print(thisEvent.hwAssigned.all())
                context = {
                    "title": title,
                    "form": form,
                    "evID": thisEvent.evID
                }

                return render(request, "events/event.html", context)

    else:

        form = eventForm(instance=thisEvent)
        form.fields['nextEvent'].queryset = event.objects.filter(start__gte= thisEvent.end)
        form.fields['hwAssigned'].queryset = hardware.objects.filter(Q(available=True, poolID__retired=False) | Q(events__evID=thisEvent.evID))
        print(thisEvent.hwAssigned.all())
        context = {
            "title": title,
            "form": form,
            "evID": thisEvent.evID
        }

        return render(request, "events/event.html", context)


class packing_pdfView(PDFTemplateView):
    template_name = "pdf/pdf_packing_rudie.html"

    def get_context_data(self, **kwargs):
        context = super(packing_pdfView, self).get_context_data(**kwargs)
        uuid = self.kwargs['uuid']
        ev = get_object_or_404(event, evID=uuid)

        context["event"] = ev

        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(packing_pdfView, self).dispatch(request, *args, **kwargs)


class srf_pdfView(PDFTemplateView):
    template_name = "pdf/pdf_srf_rudie.html"

    def get_context_data(self, **kwargs):
        context = super(srf_pdfView, self).get_context_data(**kwargs)
        uuid = self.kwargs['uuid']
        print uuid
        ev = get_object_or_404(event, evID=uuid)
        print ev
        context["event"] = ev
        context["today"] = timezone.now()
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(srf_pdfView, self).dispatch(request, *args, **kwargs)

class checkin_hardware(ListView):
    model = assignment
    template_name = 'events/checkin_hardware.html'
    paginate_by = settings.NUM_PER_PAGE
    # success_url = '/'


    def get_context_data(self, **kwargs):
        context = super(checkin_hardware, self).get_context_data(**kwargs)
        uuid = self.kwargs['uuid']
        obj_y = assignment.objects.filter(eventID=uuid)

        print obj_y.count()

        paginator = Paginator(obj_y, self.paginate_by)

        page = self.request.GET.get('page')

        try:
            obj_z = paginator.page(page)
        except PageNotAnInteger:
            obj_z = paginator.page(1)
        except EmptyPage:
            obj_z = paginator.page(paginator.num_pages)

        # print obj_z.object_list

        context['page_items'] = obj_z
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):

        if request.POST:
            if request.POST.get("_cancel"):
                    return redirect(reverse('event_edit', kwargs=self.kwargs))
            else:
                if request.POST is not None:
                    for item in request.POST.getlist('selected_hardware'):
                        print(item)
                        print(request.user)
                        print(timezone.now())
                        record = assignment.objects.get(asgID=item)
                        record.inUser = request.user
                        record.inTimeStamp = timezone.now()
                        record.save()
                    if request.POST.get("_stay"):
                        pass
                    else:
                        return redirect(reverse('event_edit', kwargs=self.kwargs))

        return super(checkin_hardware, self).dispatch(request, *args, **kwargs)

class checkout_hardware(ListView):
    model = assignment
    template_name = 'events/checkout_hardware.html'
    paginate_by = settings.NUM_PER_PAGE
    # success_url = '/'


    def get_context_data(self, **kwargs):
        context = super(checkout_hardware, self).get_context_data(**kwargs)
        uuid = self.kwargs['uuid']
        obj_y = assignment.objects.filter(eventID=uuid)

        print obj_y.count()

        paginator = Paginator(obj_y, self.paginate_by)

        page = self.request.GET.get('page')

        try:
            obj_z = paginator.page(page)
        except PageNotAnInteger:
            obj_z = paginator.page(1)
        except EmptyPage:
            obj_z = paginator.page(paginator.num_pages)

        # print obj_z.object_list

        context['page_items'] = obj_z
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):

        if request.POST:
            if request.POST is not None:
                if request.POST.get("_cancel"):
                    return redirect(reverse('event_edit', kwargs=self.kwargs))
                else:
                    for item in request.POST.getlist('selected_hardware'):
                        # print(item)
                        # print(request.user)
                        # print(timezone.now())
                        record = assignment.objects.get(asgID=item)
                        record.outUser = request.user
                        record.outTimeStamp = timezone.now()
                        record.save()
                    if request.POST.get("_stay"):
                        pass
                    else:
                        return redirect(reverse('event_edit', kwargs=self.kwargs))

        return super(checkout_hardware, self).dispatch(request, *args, **kwargs)



###############################################
##DONE CCS
@login_required
def new_hardware(request):
    title = 'New Hardware'
    form = hardwareForm(request.POST or None, initial={'poolID': get_default_pool()})

    if request.POST:


        if request.POST.get("_cancel"):
            return redirect(reverse('hardware_list'))

        else:
            form = hardwareForm(request.POST)
            if form.is_valid():
                form.save()
                obj = form.instance

                if request.POST.get("_stay"):
                    return redirect(reverse('hardware_edit', kwargs={'uuid': obj.pk} ))

                else:
                    return redirect(reverse('hardware_list'))

            else:
                context = {
                "title": title,
                    "form": form
                }

                return render(request, "hardware/hardware.html", context)


    else:
        context = {
            "title": title,
            "form": form
        }

        return render(request, "hardware/hardware.html", context)

@login_required
def multiNewHardware(request):
    title = 'Multi New Hardware'
    form = multiHardwareForm(request.POST or None, initial={'poolID': get_default_pool()})

    if request.POST:
        if request.POST.get("_cancel"):
            return redirect(reverse('hardware_list'))

        else:
            if form.is_valid():
                data = form.cleaned_data
                snlist = data['snList'].splitlines()
                for line in snlist:
                    hw = hardware(serialNum=line)

                    if data['desc']:
                        hw.desc = data['desc']

                    if data['config']:
                        hw.config = data['config']

                    if data['type']:
                        hw.type = data['type']

                    if data['poolID']:
                        hw.poolID = data['poolID']

                    if data['cost']:
                        hw.cost = data['cost']

                    hw.save()

                return redirect(reverse('hardware_list'))

            else:
                context = {
                "title": title,
                "form": form
            }

                return render(request, "hardware/multiHardware.html", context)

    else:
        context = {
            "title": title,
            "form": form
        }

        return render(request, "hardware/multiHardware.html", context)

##DONE CCS
@login_required
def edit_hardware(request, uuid=None):
    title = 'Edit Hardware'
    if uuid:
        thisObj = get_object_or_404(hardware, hwID=uuid)

    if request.POST:
        if request.POST.get("_cancel"):
            return redirect(reverse('hardware_list'))
        else:
            form = hardwareForm(request.POST, instance=thisObj)
            if form.is_valid():
                form.save()

                if request.POST.get("_stay"):
                    context = {"title": title,
                                "form": form}
                    return render(request, "hardware/hardware.html", context)

                else:
                    return redirect(reverse('hardware_list'))

            else:
                context = {"title": title,
                           "form": form}

                return render(request, "hardware/hardware.html", context)

    else:
        form = hardwareForm(instance=thisObj)

        context = {"title": title,
                    "form": form}

        return render(request, "hardware/hardware.html", context)

# @login_required
class list_hardware(ListView):

    model = hardware
    template_name = 'hardware/hw.html'
    paginate_by = settings.NUM_PER_PAGE


    def get_context_data(self, **kwargs):
        context = super(list_hardware, self).get_context_data(**kwargs)
        obj_y = hardware.objects.all()


        context['page_items'] = obj_y
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(list_hardware, self).dispatch(request, *args, **kwargs)

###############################################
## DONE CCS
@login_required
def new_contact(request):
    title = 'New Contact'
    form = contactForm(request.POST or None)

    if request.POST:
        if request.POST.get("_cancel"):
            return redirect(reverse('contact_list'))
        else:
            form = contactForm(request.POST)
            if form.is_valid():
                form.save()
                obj = form.instance

                if request.POST.get("_stay"):
                    return redirect(reverse('contact_edit', kwargs={'uuid': obj.pk} ))
                else:
                    return redirect(reverse('contact_list'))
            else:
                context = {"title": title,
                            "form": form}
                return render(request, "contact/contact.html", context)

    context = {
        "title": title,
        "form": form
    }

    return render(request, "contact/contact.html", context)

##DONE CCS
@login_required
def edit_contact(request, uuid=None):
    title = 'Edit Contact'
    if uuid:
        thisObj = get_object_or_404(contact, ctID=uuid)

    if request.POST:
        if request.POST.get("_cancel"):
            return redirect(reverse('contact_list'))

        else:
            form = contactForm(request.POST, instance=thisObj)
            if form.is_valid():
                form.save()
                if request.POST.get("_stay"):
                    context = {"title": title,
                                "form": form}
                    return render(request, "contact/contact.html", context)
                else:
                    return redirect(reverse('contact_list'))
            else:
                context = {"title": title,
                            "form": form}
                return render(request, "contact/contact.html", context)
    else:
        form = contactForm(instance=thisObj)

        context = {
            "title": title,
            "form": form
        }

        return render(request, "contact/contact.html", context)


##TODO add title context to view

class list_contact(ListView):

    model = contact
    template_name = 'contact/c.html'
    paginate_by = settings.NUM_PER_PAGE


    def get_context_data(self, **kwargs):
        context = super(list_contact, self).get_context_data(**kwargs)
        obj_y = contact.objects.all()


        context['page_items'] = obj_y
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(list_contact, self).dispatch(request, *args, **kwargs)


###############################################
##DONE CCS
@login_required
def new_airbill(request):
    title = 'New Airbill'
    form = airbillForm(request.POST or None)

    if request.POST:
        if request.POST.get("_cancel"):
            return redirect(reverse('airbill_list'))
        else:
            form = airbillForm(request.POST)
            if form.is_valid():
                form.save()
                obj = form.instance

                if request.POST.get("_stay"):
                    return redirect(reverse('airbill_edit', kwargs={'uuid': obj.pk} ))
                else:
                    return redirect(reverse('airbill_list'))
            else:
                context = {"title": title,
                            "form": form}
                return render(request, "airbill/airbill.html", context)
    else:
        context = {"title": title,
                    "form": form}
        return render(request, "airbill/airbill.html", context)

##DONECCS
@login_required
def edit_airbill(request, uuid=None):
    title = 'Edit Airbill'
    if uuid:
        thisObj = get_object_or_404(airbill, abID=uuid)

    if request.POST:
        if request.POST.get("_cancel"):
            return redirect(reverse('airbill_list'))

        else:
            form = airbillForm(request.POST, instance=thisObj)
            if form.is_valid():
                form.save()
                if request.POST.get("_stay"):
                    context = {"title": title,
                            "form": form}
                    return render(request, "airbill/airbill.html", context)
                else:
                     return redirect(reverse('airbill_list'))
            else:
                context = {"title": title,
                            "form": form}
                return render(request, "airbill/airbill.html", context)

    else:
        form = airbillForm(instance=thisObj)

    # print thisObj


    context = {
        "title": title,
        "form": form
    }

    return render(request, "airbill/airbill.html", context)


class list_airbill(ListView):

    model = airbill
    template_name = 'airbill/ab.html'
    paginate_by = settings.NUM_PER_PAGE


    def get_context_data(self, **kwargs):
        context = super(list_airbill, self).get_context_data(**kwargs)
        obj_y = airbill.objects.all()
        # #print obj_y.count()
        # paginator = Paginator(obj_y, self.paginate_by)
        #
        # page = self.request.GET.get('page')
        #
        # try:
        #     obj_z = paginator.page(page)
        # except PageNotAnInteger:
        #     obj_z = paginator.page(1)
        # except EmptyPage:
        #     obj_z = paginator.page(paginator.num_pages)
        #
        # #print obj_z.object_list

        context['page_items'] = obj_y
        return context


    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(list_airbill, self).dispatch(request, *args, **kwargs)

###############################################
##DONE CCS
@login_required
def new_pool(request):
    title = 'New Pool'
    form = poolForm(request.POST or None)

    if request.POST:
        if request.POST.get("_cancel"):
            return redirect(reverse('pool_list'))

        else:
            form = poolForm(request.POST)
            if form.is_valid():
                form.save()
                obj = form.instance

                if request.POST.get("_stay"):
                    return redirect(reverse('pool_edit', kwargs={'uuid': obj.pk} ))
                else:
                    return redirect(reverse('pool_list'))
            else:
                context = {"title": title,
                            "form": form}
                return render(request, "pool/pool.html", context)


    else:
        context = {"title": title,
                    "form": form}
        return render(request, "pool/pool.html", context)

## DONE CCS
@login_required
def edit_pool(request, uuid=None):
    title = 'Edit Pool'
    if uuid:
        thisObj = get_object_or_404(pool, poolID=uuid)

    if request.POST:
         if request.POST.get("_cancel"):
            return redirect(reverse('pool_list'))


         else:
            form = poolForm(request.POST, instance=thisObj)
            if form.is_valid():
                form.save()
                if request.POST.get("_stay"):
                    context = {"title": title,
                                "form": form}
                    return render(request, "pool/pool.html", context)
                else:
                    return redirect(reverse('pool_list'))
            else:
                context = {"title": title,
                            "form": form}
            return render(request, "pool/pool.html", context)


    else:
        form = poolForm(instance=thisObj)

        context = {"title": title,
                "form": form}
        return render(request, "pool/pool.html", context)


class list_pool(ListView):

    model = pool
    template_name = 'pool/p.html'
    paginate_by = settings.NUM_PER_PAGE


    def get_context_data(self, **kwargs):
        context = super(list_pool, self).get_context_data(**kwargs)
        obj_y = pool.objects.all()
        #print obj_y.count()
        # paginator = Paginator(obj_y, self.paginate_by)
        #
        # page = self.request.GET.get('page')
        #
        # try:
        #     obj_z = paginator.page(page)
        # except PageNotAnInteger:
        #     obj_z = paginator.page(1)
        # except EmptyPage:
        #     obj_z = paginator.page(paginator.num_pages)
        #
        # #print obj_z.object_list

        context['page_items'] = obj_y
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(list_pool, self).dispatch(request, *args, **kwargs)


###############################################


@login_required
def new_config(request):
    title = 'New Config'
    form = configForm(request.POST or None)

    if request.POST:
        if request.POST.get("_cancel"):
            return redirect(reverse('config_list'))

        else:
            form = configForm(request.POST)
            if form.is_valid():
                form.save()
                obj = form.instance

                if request.POST.get("_stay"):
                    return redirect(reverse('config_edit', kwargs={'uuid': obj.pk} ))
                else:
                    return redirect(reverse('config_list'))
            else:
                context = {"title": title,
                            "form": form}
                return render(request, "config/config.html", context)


    else:
        context = {"title": title,
                    "form": form}
        return render(request, "config/config.html", context)


@login_required
def edit_config(request, uuid=None):
    title = 'Edit Config'
    if uuid:
        thisObj = get_object_or_404(configuration, cfgID=uuid)

    if request.POST:
         if request.POST.get("_cancel"):
            return redirect(reverse('config_list'))


         else:
            form = configForm(request.POST, instance=thisObj)
            if form.is_valid():
                form.save()
                if request.POST.get("_stay"):
                    context = {"title": title,
                                "form": form}
                    return render(request, "config/config.html", context)
                else:
                    return redirect(reverse('config_list'))
            else:
                context = {"title": title,
                            "form": form}
            return render(request, "config/config.html", context)


    else:
        form = configForm(instance=thisObj)

        context = {"title": title,
                    "form": form}
        return render(request, "config/config.html", context)


class list_config(ListView):

    model = configuration
    template_name = 'config/cfg.html'
    paginate_by = settings.NUM_PER_PAGE


    def get_context_data(self, **kwargs):
        context = super(list_config, self).get_context_data(**kwargs)
        obj_y = configuration.objects.all()


        context['page_items'] = obj_y
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(list_config, self).dispatch(request, *args, **kwargs)


##############################################
##TODO Remove Example view and Templates

class HelloPDFView(PDFTemplateView):
    template_name = "pdf/hello.html"

    def get_context_data(self, **kwargs):
        self.evID = self.kwargs['evid']