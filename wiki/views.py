from django.shortcuts import render

# Create your views here.
def help_home(request):
    return render(request, "wiki/home.html")

def help_event(request):
    return render(request, "wiki/event.html")

def help_processing(request):
    return render(request, "wiki/proc.html")

def help_hardware(request):
    return render(request, "wiki/hardware.html")

def help_pool(request):
    return render(request, "wiki/pool.html")

def help_contact(request):
    return render(request, "wiki/contact.html")
