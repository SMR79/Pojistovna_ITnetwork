from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


# model pro pojistence
# navazani na model User, aby pojistenci mohli mít další informace
class InsuredPerson(models.Model):    
    """
    Model pro pojistence, který dědí z modelu User.
    Tento model obsahuje další informace o pojistenci, jako např. datum narození atd.
    """
    # Propojení InsuredPerson s User pomocí OneToOneField
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL)
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)  # E-mail by měl být unikátní pro každého pojistence    
    date_of_birth = models.DateField(null=True)
    telephone_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)        
    birth_certificate_number = models.CharField(max_length=11, unique=True, null=True, blank=True)  # Např. 123456/7890
    company_registration_number = models.CharField(max_length=20, unique=True, null=True, blank=True)  # Např. IČO pro podnikatele        
    date_registration = models.DateTimeField(auto_now_add=True) # Datum registrace pojistence
    date_last_modification = models.DateTimeField(auto_now=True) # Datum poslední úpravy pojistence        

    def __str__(self):
        return f"Pojistenec: {self.name} {self.surname} (ID: {self.id})"
    
    class Meta:
        verbose_name = "Insured person"
        verbose_name_plural = "Insured persons"



class InsuranceType(models.Model):    
    insurance_name = models.CharField(max_length=100, verbose_name="Název pojištění")
    insurance_description = models.TextField(verbose_name="Popis pojištění")
    is_active = models.BooleanField(default=False, verbose_name="Aktivní")

    def __str__(self):
        return f"{self.insurance_name}"
    
    class Meta:
        verbose_name = "Insurance Type"
        verbose_name_plural = "Insurance Types"
        ordering = ['insurance_name']



class Insurance(models.Model):
    """
    Model pro pojištění, které mohou mít pojištěnci.
    """
    # Propojení s pojistencem a typem pojištění
    insured_person = models.ForeignKey(InsuredPerson, on_delete=models.CASCADE, related_name='insurances')
    insurance_type = models.ForeignKey(InsuranceType, on_delete=models.CASCADE, related_name='insurances')    
    insurance_number = models.CharField(max_length=20, unique=True, default=uuid.uuid4())  # Unikátní identifikátor pojištění, generovaný UUID
    insurance_subject = models.CharField(max_length=30, verbose_name="Insurance subject", null=True, blank=True)
    insurance_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Insurance price", default=100)
    start_date = models.DateField(auto_now_add=True)  # Datum začátku pojištění
    end_date = models.DateField(null=True, blank=True)  # Datum konce pojištění (pokud je relevantní)
    is_active = models.BooleanField(default=True)  # Stav pojištění

    def __str__(self):
        return f"{self.insured_person.name} {self.insured_person.surname} - {self.insurance_type}"

    class Meta:
        verbose_name = "Insurance"
        verbose_name_plural = "Insurances"
        ordering = ['-start_date']

class Event(models.Model):
    """
    Model pro události spojené s pojištěním.
    """
    insurance = models.ForeignKey(Insurance, on_delete=models.CASCADE, related_name='events')
    event_date = models.DateTimeField(auto_now_add=True)  # Datum a čas události
    report_date = models.DateTimeField(default=timezone.now)  # Datum a čas nahlášení události
    description = models.TextField()  # Popis události
    damage_amount = models.DecimalField(decimal_places=2, max_digits=10, default=0.00)  # výše škody
    payment_amount = models.DecimalField(decimal_places=2, max_digits=9, default=0.00)  # výše vyplacené částky(pokud schváleno)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Událost {self.id} pro pojištění {self.insurance.insurance_number} - {self.event_date.strftime('%Y-%m-%d %H:%M:%S')}"
    
    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        ordering = ['-event_date']