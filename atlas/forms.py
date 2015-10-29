from django import forms
from .models import event
from django.forms.widgets import SplitDateTimeWidget
from datetimewidget.widgets import DateTimeWidget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from crispy_forms.bootstrap import StrictButton
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


class login(forms.Form):
    username = forms.CharField(
        label=u'Username',
        required=True,
    )
    password = forms.CharField(
        label=u'Login',
        required=True,
        widget=forms.PasswordInput
    )
    remember_me = forms.BooleanField(
        label=u'Remember me',
        required=True
    )
    def __init__(self, *args, **kwargs):
        super(login, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            'username',
            'password',
            'remember_me',
            StrictButton('Sign in', css_class='btn-default'),

        )