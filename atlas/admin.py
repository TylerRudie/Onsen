from django.contrib import admin
from datetime import *
from .models import *
from django.contrib.contenttypes.admin import GenericTabularInline


class assingmentInline(admin.TabularInline):
    model = assignment
    extra = 0
    verbose_name = 'Assigments'

class ctEventID(admin.TabularInline):
    model = event.ctAssigned.through
    extra = 0
    verbose_name = 'Assigned Contact'

class abEvent(admin.TabularInline):
    model = event.abAssigned.through
    extra = 0
    verbose_name = 'Assigned Airbill'


class HardwareAdmin(admin.ModelAdmin):

    fields = ['serialNum','desc','config','poolID']
    inlines = [assingmentInline,]


class EventAdmin(admin.ModelAdmin):
    model = event
    #fields = ['name','status','startDate','endDate','hwAssigned' ]

    inlines = [ctEventID, assingmentInline, abEvent]
    list_display = ['title', 'start', 'end']
    ordering = ['start']
    list_filter = ['start']

admin.site.register(event, EventAdmin)
admin.site.register(contact )
admin.site.register(hardware, HardwareAdmin)
admin.site.register(contact_event)
admin.site.register(airbill)
admin.site.register(case)
admin.site.register(pool)
admin.site.register(event_airbill)
# Register your models here.
