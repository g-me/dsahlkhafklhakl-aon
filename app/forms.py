from django import forms
from django.contrib.auth.models import User

from app.models import Request, UserProfile


class ProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Request
        fields = ('title', 'description', 'skills',)


class ProfileForm(forms.ModelForm):
    skills = forms.CharField()

    class Meta:
        model = UserProfile
        fields = ('career', 'company', 'website', 'about', 'location', 'stackoverflow_account', 'github_account',
                  'twitter_account', 'google_plus_account')

class AccountUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
