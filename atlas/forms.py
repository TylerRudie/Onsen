from django import forms
from .models import event, hardware, contact, airbill, pool
from bootstrap3_datetime.widgets import DateTimePicker
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from crispy_forms.bootstrap import TabHolder, Tab, AppendedText, PrependedText, FormActions
from better_filter_widget import BetterFilterWidget
## TODO finish filling out form data

class eventForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_tag = False
    helper.layout = Layout(
        TabHolder(
            Tab(
                'Basic Information',
                'title',
                'start',
                'end',
                'all_day',
                'nextEvent',
                'pool',

            ),
            Tab(
                'Shipping',

                'dateShipped',
                'abAssigned',
                'caseAssigned'
            ),
            Tab(
                'Details',
                'site',
                'laptopsRequested',
                'projectorRequested',
                'configAssigned',
                'limbo',

            ),
            Tab(
                'Contacts',
                'shipping_contact',
                'instructor_contact'
            ),
            Tab(
                'Hardware',
                'hwAssigned',
            ),

        )
    )

    def __init__(self, *args, **kwargs):
        super(eventForm, self).__init__(*args, **kwargs)


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

            'dateShipped': DateTimePicker(options={"format": "YYYY-MM-DD",
                                                   "pickSeconds": False
                                                   }),
            'hwAssigned': BetterFilterWidget(),
            'caseAssigned': BetterFilterWidget(),
            'abAssigned': BetterFilterWidget(),
            'instructor_contact': BetterFilterWidget(),
        }
        readonly_fields = ['Transition_To_Event']

##TODO add save, and save and return buttons
class hardwareForm(forms.ModelForm):

    class Meta:
        model = hardware
        exclude = ['hwID','available' ]


class multiHardwareForm(forms.ModelForm):

    snList = forms.CharField(widget=forms.Textarea)
    snList.label = 'List of Serial Numbers'

    def __init__(self, *args, **kwargs):
        super(multiHardwareForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Create Multiple New Hardware',
                'snList',
                'desc',
                'config',
                'type',
                'poolID',
                FormActions(
                    Submit('_submit', 'Submit', css_class="btn-primary"),
                    Submit('_cancel', 'Cancel'),
                    )
            ),

        )


    class Meta:
        model = hardware
        exclude = ['hwID','available','serialNum']



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