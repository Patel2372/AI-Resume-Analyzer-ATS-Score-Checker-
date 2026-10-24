from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import JobDescription, Resume, ResumeVersion


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ('title', 'file')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Python Developer Resume'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf,.docx'}),
        }

    def clean_file(self):
        uploaded = self.cleaned_data['file']
        ext = uploaded.name.lower().rsplit('.', 1)[-1]
        if ext not in {'pdf', 'docx'}:
            raise forms.ValidationError('Only PDF and DOCX files are supported.')
        if uploaded.size > 5 * 1024 * 1024:
            raise forms.ValidationError('Maximum file size is 5 MB.')
        return uploaded


class JobDescriptionForm(forms.ModelForm):
    class Meta:
        model = JobDescription
        fields = ('title', 'company', 'description')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Python Developer'}),
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company name (optional)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 14, 'placeholder': 'Paste the full job description here...'}),
        }


class ResumeVersionForm(forms.ModelForm):
    class Meta:
        model = ResumeVersion
        fields = ('version_name', 'note')
        widgets = {
            'version_name': forms.TextInput(attrs={'class': 'form-control'}),
            'note': forms.TextInput(attrs={'class': 'form-control'}),
        }


class RewriteForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 6}))
    context = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Python Developer project'}))
