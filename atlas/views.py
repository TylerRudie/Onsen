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

from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse

from .forms import eventForm, hardwareForm, contactForm, airbillForm, poolForm, multiHardwareForm, configForm
from .models import event, hardware, contact, airbill, pool, assignment, configuration

## TODO Setup reverse on all submit views
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
def home(request):

    context = {
            "title": 'Home',
            "laptop_usage": get_hw_staus_stats(hwType='Laptop'),
            "projector_usage": get_hw_staus_stats(hwType='Test')
        }
    return render(request, "home.html", context)

def draw_graph(request, x="None"):
    total = hardware.objects.filter(type=x).count()
    inuse = hardware.objects.filter(type=x).filter(available=1).count()
    percent = (inuse/total)*100

    graph_data = []

    avail_data = {}
    avail_data["value"] = percent
    avail_data["label"] =  x+"(s)"" Available"
    graph_data.append(avail_data)

    unavail_data = {}
    unavail_data["value"] = percent-100
    unavail_data["label"] =  x+"(s)"+" Unavailable"
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
    form = eventForm(request.POST or None, initial={'pool': df,
                                                    'seat_revenue': df.default_seat_revenue,
                                                    'projector_revenue': df.default_projector_revenue})
    form.fields['nextEvent'].queryset = event.objects.none()
    form.fields['hwAssigned'].queryset = hardware.objects.filter(available=True)
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
                if request.POST.get("_stay"):
                    form = eventForm(instance=thisEvent)
                    form.fields['nextEvent'].queryset = event.objects.filter(start__gte= thisEvent.end)
                    form.fields['hwAssigned'].queryset = hardware.objects.filter(Q(available=True) | Q(events__evID=thisEvent.evID))
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
                form.fields['hwAssigned'].queryset = hardware.objects.filter(Q(available=True) | Q(events__evID=thisEvent.evID))
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
        form.fields['hwAssigned'].queryset = hardware.objects.filter(Q(available=True) | Q(events__evID=thisEvent.evID))
        print(thisEvent.hwAssigned.all())
        context = {
            "title": title,
            "form": form,
            "evID": thisEvent.evID
        }

        return render(request, "events/event.html", context)


class packing_pdfView(PDFTemplateView):
    template_name = "pdf/pdf_packing.html"

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
    template_name = "pdf/pdf_srf.html"

    def get_context_data(self, **kwargs):
        context = super(srf_pdfView, self).get_context_data(**kwargs)
        uuid = self.kwargs['uuid']
        print uuid
        ev = get_object_or_404(event, evID=uuid)
        print ev
        context["event"] = ev
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