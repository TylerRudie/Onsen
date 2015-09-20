from django.contrib import admin

from .models import event, hardware, contact, contact_event


class EventInline(admin.StackedInline):
    model = event.hwAssigned.through
    extra = 1


class ctEventID(admin.TabularInline):
    model = event.ctAssigned.through
    extra = 1
    verbose_name = 'Assigned Contact'

class HardwareAdmin(admin.ModelAdmin):
    fields = ['serialNum','desc','config','status']
    inlines = [EventInline]


class EventAdmin(admin.ModelAdmin):
    fields = ['name','status','startDate','endDate','hwAssigned']
    inlines = [ctEventID]


admin.site.register(event, EventAdmin)
admin.site.register(contact )
admin.site.register(hardware, HardwareAdmin)
admin.site.register(contact_event)
# Register your models here.
