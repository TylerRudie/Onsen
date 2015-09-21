from django.contrib import admin

from .models import *


class EventInline(admin.StackedInline):
    model = event.hwAssigned.through
    extra = 0


class ctEventID(admin.TabularInline):
    model = event.ctAssigned.through
    extra = 0
    verbose_name = 'Assigned Contact'

class abEvent(admin.TabularInline):
    model = event.abAssigned.through
    extra = 0
    verbose_name = 'Assigned Airbill'


class HardwareAdmin(admin.ModelAdmin):
    fields = ['serialNum','desc','config','status']
    inlines = [EventInline]


class EventAdmin(admin.ModelAdmin):
    fields = ['name','status','startDate','endDate','hwAssigned']
    inlines = [ctEventID, abEvent]


admin.site.register(event, EventAdmin)
admin.site.register(contact )
admin.site.register(hardware, HardwareAdmin)
admin.site.register(contact_event)
admin.site.register(airbill)
admin.site.register(event_airbill)
# Register your models here.
