from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import InsuredPerson, InsuranceType, Event, Insurance
from dal import autocomplete


class InsuredPersonForm(forms.ModelForm):
    class Meta:
        model = InsuredPerson
        fields = [    
            'name',
            'surname',                   
            'date_of_birth',
            'birth_certificate_number',            
            'address',
            'email',
            'telephone_number',
            'company_registration_number',  # Pro podnikatele
        ]
        labels = {    
            'name': 'Jméno',
            'surname': 'Příjmení',
            'date_of_birth': 'Datum narození',
            'birth_certificate_number': 'Rodné číslo',
            'telephone_number': 'Telefon',
            'address': 'Adresa',
            'email': 'E-mail',             
            'company_registration_number': 'IČO (pro podnikatele)',                    
        }
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'telephone_number': forms.TextInput(attrs={'placeholder': '+420123456789'}),
            'address': forms.TextInput(attrs={'placeholder': 'Ulice, Město, PSČ'}),
        }


class InsuredPersonRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')
        help_texts = {
            'password1': '''
                • Minimálně 8 znaků
                • Nesmí být běžně používané
                • Nesmí obsahovat pouze čísla
                • Nesmí být podobné vašim osobním údajům
            ''',
            'password2': 'Pro ověření zadejte heslo znovu',
        }


class AddInsuranceTypeForm(forms.ModelForm):
    class Meta:
        model = InsuranceType
        fields = ['insurance_name', 'insurance_description', 'is_active']
        labels = {
            'insurance_name': 'Název pojištění',
            'insurance_description': 'Popis pojištění',
            'is_active': 'Aktivní',
        }
        widgets = {
            'insurance_description': forms.Textarea(attrs={'rows': 4}),
        }


class InsuranceForm(forms.ModelForm):
    class Meta:
        model = Insurance
        fields = ['insurance_type', 'insurance_subject', 'insurance_price', 'is_active']
        labels = {
            'insurance_type': 'Typ pojištění',
            'insurance_subject': 'Předmět pojištění',
            'insurance_price': 'Cena pojištění',            
            'is_active': 'Aktivní',
        }
        widgets = {
            'insurance_subject': forms.TextInput(attrs={'placeholder': 'Např. automobil, dům...'}),
            'insurance_price': forms.NumberInput(attrs={'step': 1, 'min': 0}),
        }


class AddEventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['insurance', 'description', 'damage_amount']
        labels = {
            'insurance': 'Pojištění (dle pojištěnce)',
            'description': 'Popis události',
            'damage_amount': 'Výše škody (Kč)',
        }
        widgets = {
           'insurance': autocomplete.ModelSelect2(url='pojistovna:insurance-autocomplete'),
           'description': forms.Textarea(attrs={'rows': 3}),
        }



class SuperUserCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Heslo")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.is_staff = True
        user.is_superuser = True
        if commit:
            user.save()
        return user
    

class StaffUserCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Heslo")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.is_staff = True
        user.is_superuser = False
        if commit:
            user.save()
        return user
    

