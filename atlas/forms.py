from django import forms
from .models import event, hardware, contact, airbill, pool
from bootstrap3_datetime.widgets import DateTimePicker
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from crispy_forms.bootstrap import StrictButton


class eventForm(forms.ModelForm):
    class Meta:
        model = event
        exclude = ['evID', 'status']
        # Fixed DateTime Picker is not accepting options or 2nd or 3rd instance
        widgets = {
            'start': DateTimePicker(options={"format": "YYYY-MM-DD HH:mm",
                                             "pickSeconds": False
                                             }),

            'end': DateTimePicker(options={"format": "YYYY-MM-DD HH:mm",
                                           "pickSeconds": False
                                           }),

            'dateShipped': DateTimePicker(options={"format": "YYYY-MM-DD HH:mm",
                                                   "pickSeconds": False
                                                   })
        }
        readonly_fields = ['Transition_To_Event']

##TODO add save, and save and return buttons
class hardwareForm(forms.ModelForm):
    class Meta:
        model = hardware
        exclude = ['hwID', ]


class contactForm(forms.ModelForm):
    class Meta:
        model = contact
        exclude = ['cdID', ]


class airbillForm(forms.ModelForm):
    class Meta:
        model = airbill
        exclude = ['abID', ]

class poolForm(forms.ModelForm):
    class Meta:
        model = pool
        exclude = ['poolID', ]