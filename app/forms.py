from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from app.models import Profile, City, Bicycle, Citizenship, CitizenshipType, OFC, ArchiveFile, Executor, Contact, \
    ExecutorConfig, UserPayment


#
#                           City Forms
#
class CityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ['name']


#
#                           User Forms
#
class UserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'last_name', 'first_name', 'email', 'password1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields['password2']


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'last_name', 'first_name', 'email', 'password']


class CuratorUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['last_name', 'first_name', 'email']


class CuratorProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['patronymic', 'phone_number']


class CuratorPaymentForm(forms.ModelForm):
    class Meta:
        model = UserPayment
        fields = ['payment_for_internship_hours', 'payment_for_initial_hours']


class ProfileCreateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['patronymic', 'phone_number', 'password1', 'role']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['patronymic', 'phone_number', 'role']


#
#                           Bicycle Forms
#
class BicycleForm(forms.ModelForm):
    class Meta:
        model = Bicycle
        fields = ['name']


#
#                           Citizenship Forms
#
class CitizenshipForm(forms.ModelForm):
    class Meta:
        model = Citizenship
        fields = ['name']


#
#                           Citizenship Forms
#
class CitizenshipTypeForm(forms.ModelForm):
    class Meta:
        model = CitizenshipType
        fields = ['name']


#
#                           OFC Forms
#
class OFCForm(forms.ModelForm):
    class Meta:
        model = OFC
        fields = ['address', 'code', 'city']


#
#                           ArchiveFile Forms
#
class ArchiveFileForm(forms.ModelForm):
    class Meta:
        model = ArchiveFile
        fields = ['file', 'description', 'type']


class ArchiveFileUpdateForm(forms.ModelForm):
    class Meta:
        model = ArchiveFile
        fields = ['description', 'type']


#
#                           Executor Forms
#
class ExecutorForm(forms.ModelForm):
    class Meta:
        model = Executor
        fields = '__all__'


#
#                           Contact Forms
#
class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['identifier', 'type']


#
#                           Config Forms
#
class ExecutorConfigForm(forms.ModelForm):
    class Meta:
        model = ExecutorConfig
        fields = '__all__'
