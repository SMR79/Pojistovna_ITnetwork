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
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if InsuredPerson.objects.filter(email=email).exists():
            raise forms.ValidationError("Tento e-mail již evidujeme.")
        return email

    def clean_birth_certificate_number(self):
        rc = self.cleaned_data.get('birth_certificate_number')

        if not rc:
            raise forms.ValidationError("Rodné číslo je povinné.")  # pokud má být povinné

        if not rc.isdigit():
            raise forms.ValidationError("Rodné číslo musí obsahovat pouze číslice.")
        if len(rc) not in [9, 10]:
            raise forms.ValidationError("Rodné číslo musí mít 9 nebo 10 číslic.")
        return rc

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name and not name.replace(" ", "").isalpha():
            raise forms.ValidationError("Jméno smí obsahovat pouze písmena a mezery.")
        return name

    def clean_surname(self):
        surname = self.cleaned_data.get('surname')
        if surname and not surname.replace(" ", "").isalpha():
            raise forms.ValidationError("Příjmení smí obsahovat pouze písmena a mezery.")
        return surname

    def clean_telephone_number(self):
        import re
        tel = self.cleaned_data.get('telephone_number')
        if tel and not re.match(r'^\+420\d{9}$', tel):
            raise forms.ValidationError("Telefonní číslo musí být ve formátu +420XXXXXXXXX.")
        return tel

    def clean_company_registration_number(self):
        ico = self.cleaned_data.get('company_registration_number')
        if ico and (not ico.isdigit() or len(ico) != 8):
            raise forms.ValidationError("IČO musí mít přesně 8 číslic.")
        return ico

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        surname = cleaned_data.get('surname')
        date_of_birth = cleaned_data.get('date_of_birth')

        if name and surname and date_of_birth:
            if InsuredPerson.objects.filter(
                name=name,
                surname=surname,
                date_of_birth=date_of_birth
            ).exists():
                raise forms.ValidationError("Pojištěnec se stejným jménem, příjmením a datem narození již existuje.")

        return cleaned_data


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
    

