from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import StudentProfile,AppliedJob

class SignUpForm(UserCreationForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ('username', 'email', 'password1')
        def __init__(self, *args, **kwargs):
            super(SignUpForm, self).__init__(*args, **kwargs)
            if 'password2' in self.fields:
                del self.fields['password2']

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = '__all__'
        exclude = ['user', 'plan']
        
        
class AppliedJobForm(forms.ModelForm):
    class Meta:
        model = AppliedJob
        fields = ['user',  'job_link', 'resume', 'applied_date']
        widgets = {
            'job_link': forms.URLInput(attrs={'class': 'form-control'}),
            'resume': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'applied_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'user': forms.Select(attrs={'class': 'form-select'}),
        }
        
        