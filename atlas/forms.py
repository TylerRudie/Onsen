from django import forms
from .models import event
from django.forms.widgets import SplitDateTimeWidget
from datetimewidget.widgets import DateTimeWidget

class eventForm(forms.ModelForm):



    class Meta:
        model = event
        exclude = ['evID','status']
        # TODO DateTime Picker is not accepting options or 2nd or 3rd instance
        widgets = {
            'start': DateTimeWidget(attrs={'id':"yourdatetimeid"},
                                   usel10n = True,
                                   bootstrap_version=3),

            'end': DateTimeWidget(attrs={'id':"yourdatetimeid"},
                                   usel10n = True,
                                   bootstrap_version=3),

            'dateShipped': DateTimeWidget(attrs={'id':"yourdatetimeid"},
                                   usel10n = True,
                                   bootstrap_version=3),
        }
