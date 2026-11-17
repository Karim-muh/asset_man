from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
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
        fields = '__all__'


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


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=150,widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'Enter your first name'}))
    last_name = forms.CharField(max_length=150,widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'Enter your last name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control','placeholder': 'Enter your email'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = User
        fields = ['username','first_name','last_name','email']

