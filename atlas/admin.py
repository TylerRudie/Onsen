from django.contrib import admin

from .models import event, hardware

admin.site.register(event)

admin.site.register(hardware)

# Register your models here.
