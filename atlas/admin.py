from django.contrib import admin
from datetime import *
from .models import *
from django.contrib.contenttypes.admin import GenericTabularInline


class assingmentInline(admin.StackedInline):
    model = assignment
    # readonly_fields= ['eventID_start', ]
    extra = 0
    verbose_name = 'Assignments'


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
    # fields= ('title', 'start', 'end', 'all_day', 'TranToEvent' )

    inlines = [ctEventID,  abEvent,]
    list_display = ['title', 'start', 'end',  'Transition_To_Event', 'Transition_from_event']
    readonly_fields=['Transition_To_Event', 'Transition_from_event', 'url']
    filter_horizontal = ('hwAssigned','caseAssigned')
    ordering = ['start']
    list_filter = ['start']
    search_fields = ['title']
    # filter_horizontal = ['hwAssigned',]

admin.site.register(event, EventAdmin)
admin.site.register(contact )
admin.site.register(hardware, HardwareAdmin)
admin.site.register(contact_event)
admin.site.register(airbill)
admin.site.register(case)
admin.site.register(pool)
admin.site.register(event_airbill)
# Register your models here.
