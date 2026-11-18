from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.forms import ModelForm
from .models import UserProfile, Asset, Requisition, Distribution, Disposal, Department, Employee


class LoginForm(forms.Form):

    username = forms.CharField( max_length=150,widget=forms.TextInput(attrs={'placeholder': 'Enter your username','class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password','class': 'form-control'}))

class UserProfileForm(ModelForm):
    
    class Meta:
        model = UserProfile
        fields = ['role', 'is_approved']


class DepartmentForm(ModelForm):

    class Meta:
        model = Department
        fields = '__all__'


class EmployeeForm(ModelForm):

    class Meta:
        model = Employee
        fields = [
            'employee_number',
            'first_name',
            'last_name',
            'email',
            'phone',
            'job_title',
            'department',
        ]


class EmployeeCreateForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password1 = forms.CharField(label='Login password', strip=False, widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm login password', strip=False, widget=forms.PasswordInput)

    class Meta:
        model = Employee
        fields = [
            'employee_number', 'first_name', 'last_name', 'email',
            'phone', 'job_title', 'department',
        ]

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('This username is already in use.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'The passwords do not match.')
        elif password1:
            candidate_user = User(
                username=cleaned_data.get('username', ''),
                email=cleaned_data.get('email', ''),
                first_name=cleaned_data.get('first_name', ''),
                last_name=cleaned_data.get('last_name', ''),
            )
            try:
                validate_password(password1, candidate_user)
            except ValidationError as error:
                self.add_error('password1', error)
        return cleaned_data


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        if Employee.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An employee record with this email already exists.')
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class AssetForm(ModelForm):

    class Meta:
        model = Asset
        fields = '__all__'


class RequisitionForm(ModelForm):

    class Meta:
        model = Requisition
        fields = '__all__'


class DistributionForm(ModelForm):

    class Meta:
        model = Distribution
        fields = '__all__'


class DisposalForm(ModelForm):

    class Meta:
        model = Disposal
        fields = '__all__'

