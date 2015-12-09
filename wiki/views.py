from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def help_home(request):
    return render(request, "wiki/home.html")

@login_required
def help_event(request):
    return render(request, "wiki/event.html")

@login_required
def help_processing(request):
    return render(request, "wiki/proc.html")

@login_required
def help_hardware(request):
    return render(request, "wiki/hardware.html")

@login_required
def help_pool(request):
    return render(request, "wiki/pool.html")

@login_required
def help_contact(request):
    return render(request, "wiki/contact.html")
