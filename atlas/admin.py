from django.contrib import admin
from datetime import *
from .models import *
from django.contrib.contenttypes.admin import GenericTabularInline


class assingmentInline(admin.StackedInline):
    model = assignment
    # readonly_fields= ['eventID_start', ]
    extra = 0
    verbose_name = 'Assignments'




class abEvent(admin.TabularInline):
    model = event.abAssigned.through
    extra = 0
    verbose_name = 'Assigned Airbill'


class HardwareAdmin(admin.ModelAdmin):

    fields = ['serialNum','desc','config','poolID']

    inlines = [assingmentInline,]
    list_display = ['serialNum','desc','status']
    search_fields = ['serialNum','desc']

class EventAdmin(admin.ModelAdmin):
    model = event
    # fields= ('title', 'start', 'end', 'all_day', 'TranToEvent' )

    inlines = [ assingmentInline ]
    list_display = ['title', 'start', 'end',  'Transition_to_event', 'Transition_from_event']
    readonly_fields=['Transition_to_event', 'Transition_from_event', 'url']
    filter_vertical = ('caseAssigned', 'configAssigned','instructor_contact')
    ordering = ['start']
    list_filter = ['start']
    search_fields = ['title']
    # filter_horizontal = ['hwAssigned',]

admin.site.register(event, EventAdmin)
admin.site.register(contact )
admin.site.register(hardware, HardwareAdmin)

admin.site.register(airbill)
admin.site.register(case)
admin.site.register(pool)
admin.site.register(event_airbill)
admin.site.register(configuration)
# Register your models here.
