from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import authenticate, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from .forms import InsuredPersonRegistrationForm, InsuredPersonForm, AddInsuranceTypeForm, AddEventForm, InsuranceForm, SuperUserCreateForm, StaffUserCreateForm  # Importujte svůj formulář pro pojistence
from .models import InsuredPerson, InsuranceType, Insurance, Event  # Importujte svůj model pojistenců
from django.core.paginator import Paginator
from decimal import InvalidOperation, Decimal
from dal import autocomplete
from uuid import uuid4

# Function to get insured persons with insurance count.
def get_insured_persons_with_insurance_count(query=None):
    qs = InsuredPerson.objects.annotate(
        insurance_count=Count('insurances')
    ).order_by('id')

    if query:
        qs = qs.filter(Q(name__icontains=query) | Q(surname__icontains=query))
    
    return qs

# Function to render home page of insurance company.
def home(request):
    # View funkce pro zobrazení domovské stránky pojišťovny.
    return render(request, 'pojistovna/home.html')


# Function to log in user.
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Přihlášení bylo úspěšné.")
            return redirect('pojistovna:home')
        else:
            messages.error(request, 'Neplatné přihlašovací údaje.')
    else:
        form = AuthenticationForm()
    return render(request, 'pojistovna/login.html', {'form': form})


# Function to log out user.
def logout_view(request):
    logout(request)
    return redirect('pojistovna:login')


# Function to register new user.
@login_required
def insured_person_register(request, id):      
    insured_person = get_object_or_404(InsuredPerson, id=id)
    
    # Pokud už je propojeno, zobraz chybovou hlášku
    if insured_person.user:
        messages.error(request, 'Tento pojištěnec již má uživatelský účet.')
        return redirect('pojistovna:insured_person_detail', id=id)
    
    if request.method == 'POST':
        form = InsuredPersonRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']

            # 1️⃣ Zkontroluj, zda uživatel s tímto emailem existuje
            existing_user = User.objects.filter(username=email).first()
            if existing_user:
                # Pokud ano, pouze propojit
                insured_person.user = existing_user
                insured_person.save()
                messages.success(request, 'Uživatel již existuje a byl propojen s pojištěncem.')
                return redirect('pojistovna:insured_person_detail', id=id)
            
            # 2️⃣ Vytvoř nový účet
            user = form.save(commit=False)
            user.username = email  # Username bude e-mail
            user.email = email
            user.save()

            # Propoj s pojištěncem
            insured_person.user = user
            insured_person.save()

            # Přihlásit nově registrovaného uživatele
            login(request, user)
            messages.success(request, 'Registrace byla úspěšná a účet byl propojen.')
            return redirect('pojistovna:insured_person_detail', id=id)
    else:
        form = InsuredPersonRegistrationForm(initial={'email': insured_person.email})
    
    return render(request, 'pojistovna/register.html', {
        'form': form,
        'insured_person': insured_person
    })


# Function to reset new password.
def user_password_reset(request, id):
    user = get_object_or_404(User, pk=id)

    if request.method == "POST":
        new_password = request.POST.get("new_password")
        if new_password:
            user.set_password(new_password)
            user.save()
            messages.success(request, f"Heslo pro uživatele {user.username} bylo úspěšně změněno.")
            if user.is_staff or user.is_superuser:
                return redirect('pojistovna:staff_and_super_list')  # Přesměrování po úspěchu
            else:
                return redirect('pojistovna:users_list')  # Přesměrování po úspěchu
        else:
            messages.error(request, "Zadejte nové heslo.")

    return render(request, 'pojistovna/user_password_reset.html', {'user': user})


# Function to remove user.
def user_delete(request, id):
    user = get_object_or_404(User, pk=id)
    if request.method == "POST":
        user.delete()
        return redirect('pojistovna:users_list')


# Function to add new insured person in database.
@login_required
def add_insured_person(request):
    # View funkce pro přidání nového pojistence.
    # Zde implementovat logiku pro přidání pojistence do databáze.       
    if request.method == 'POST':
        form = InsuredPersonForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pojistěnec byl úspěšně přidán.')
            return redirect('pojistovna:insured_person')  # Přesměrování na seznam pojistenců
    else:
        form = InsuredPersonForm()
    context = {
        'form': form
    }
    return render(request, 'pojistovna/insured_person_form.html', context)


# Function to remove insured person from database.
def insured_person_delete(request, id):
    person = get_object_or_404(InsuredPerson, pk=id)
    if request.method == "POST":
        person.delete()
        return redirect('pojistovna:insured_person') 
    

# Function to show list of insured persons users in database.
def users_list(request):
    users = User.objects.all()
    user_data = []

    for user in users:
        try:
            insured = InsuredPerson.objects.get(user=user)
            user_data.append({
                'id': user.id,
                'email': user.email,
                'name': insured.name,
                'surname': insured.surname
            })
        except InsuredPerson.DoesNotExist:
            user_data.append({
                'id': user.id,
                'email': user.email,
                'name': '(neuvedeno)',
                'surname': '(neuvedeno)'
            })
    
    paginator = Paginator(user_data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    context = {'page_obj': page_obj}
    return render(request, 'pojistovna/users_list.html', context)


# Function to show dynamicaly a list of users in database.
def dynamic_user_search(request):
    name = request.GET.get('name', '').strip().lower()
    surname = request.GET.get('surname', '').strip().lower()

    user_data = []

    users = User.objects.all()

    for one_user in users:
        try:
            insured = InsuredPerson.objects.get(user=one_user)
            if name and name not in insured.name.lower():
                continue
            if surname and surname not in insured.surname.lower():
                continue
            user_data.append({
                'id': one_user.id,
                'email': one_user.email,
                'name': insured.name,
                'surname': insured.surname
            })
        except InsuredPerson.DoesNotExist:
            if name or surname:
                continue
            user_data.append({
                'id': one_user.id,
                'email': one_user.email,
                'name': '(neuvedeno)',
                'surname': '(neuvedeno)'
            })

    paginator = Paginator(user_data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'pojistovna/users_list_partial.html', {
        'page_obj': page_obj,
        'name': name,
        'surname': surname,
    })


# Function to show list of staff or super users.
def staff_and_super_list(request):
    # View funkce pro zobrazení seznamu superuživatelů.
    # Zde byste měli získat seznam superuživatelů z databáze a předat ho do šablony.
    super_users = User.objects.filter(is_superuser=True)
    staff_users = User.objects.filter(is_staff=True)    

    # Sjednocení bez duplikátů
    staff_super_users = (super_users | staff_users).distinct()

    paginator = Paginator(staff_super_users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj}
    return render(request, 'pojistovna/staff_and_super_list.html', context)


# Function to add staff user as an operator.
def add_staff_user(request):
    
    if request.method == 'POST':
        form = StaffUserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pojistovna:staff_and_super_list')
    else:
        form = StaffUserCreateForm()
    return render(request, 'pojistovna/add_staff_user.html', {'form': form})


# Function to add staff user as an administrator.
def add_super_user(request):
    if request.method == 'POST':
        form = SuperUserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pojistovna:staff_and_super_list')
    else:
        form = SuperUserCreateForm()
    return render(request, 'pojistovna/add_super_user.html', {'form': form})


# Function to show details of insured person such as name, day of birth, etc.
def insured_person_detail(request, id):
    # View funkce pro zobrazení detailu pojistence.
    # Zde byste měli získat detail pojistence z databáze a předat ho do šablony.
    try:
        insured_person = InsuredPerson.objects.get(id=id)
    except InsuredPerson.DoesNotExist:
        messages.error(request, 'Pojistěnec nebyl nalezen.')
        return redirect('pojistovna:insured_person')

    # Získání všech pojištění spojených s tímto pojistencem    
    insurances = Insurance.objects.filter(insured_person=insured_person)

    context = {
        'insured_person': insured_person,
        'insurances': insurances,
    }
    return render(request, 'pojistovna/insured_person_detail.html', context)


# Function to edit insured person such as name, day of birth, etc.
def edit_insured_person(request, id):
    one_insured_person = InsuredPerson.objects.get(pk=id)
    if request.method == 'POST':
        form = InsuredPersonForm(request.POST, instance=one_insured_person)
        if form.is_valid():
            form.save()
            return redirect('pojistovna:insured_person')
    else:
        form = InsuredPersonForm(instance=one_insured_person)
    return render(request, 'pojistovna/insured_person_form.html', {'form': form})


# Function to show dynamicaly a list of insured persons in database.
def dynamic_insured_person_search(request):
    name = request.GET.get('name', '').strip()
    surname = request.GET.get('surname', '').strip()

    qs = InsuredPerson.objects.annotate(
        insurance_count=Count('insurances')
    )

    if name:
        qs = qs.filter(name__icontains=name)
    if surname:
        qs = qs.filter(surname__icontains=surname)

    paginator = Paginator(qs.order_by('id'), 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'pojistovna/insured_person_table_rows.html', {
        'page_obj': page_obj,
        'name': name,
        'surname': surname,
    })


# Function to show a list with  pages of 10 insured persons in database.
def insured_person_list(request):
    # Přidáme ke každému pojištěnci počet pojištění
    insured_persons = InsuredPerson.objects.annotate(
        insurance_count=Count('insurances')  # "insurance" je related_name z modelu Insurance
    ).order_by('id')  # volitelně seřazeno podle příjmení

    paginator = Paginator(insured_persons, 10)  # 10 položek na stránku
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj
    }

    return render(request, 'pojistovna/insured_person.html', context)


# Function to add an insurance to database which can be used for insured persons.
def add_insurance(request):
    # View funkce pro přidání nového pojištění.
    # Zde implementovat logiku pro přidání pojištění do databáze.
    if request.method == 'POST':
        form = AddInsuranceTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pojištění bylo úspěšně přidáno.')
            return redirect('pojistovna:insurance_list')  # Přesměrování na seznam pojištění
    else:
        form = AddInsuranceTypeForm()
    context = {
        'form': form
    }
    return render(request, 'pojistovna/add_insurance.html', context)


# Function to show insurance list.
def insurance_list(request):
    # Vytvoříme seznam obsahující název a popis
    available_insurances = InsuranceType.objects.all().order_by('-is_active', 'insurance_name')
    context = {
        'available_insurances': available_insurances
    }
    return render(request, 'pojistovna/insurance_list.html', context)


# Function to switch active/deactive status of the type of insurance.
def toggle_insurance_status(request, id, activate=True):
    insurance_type = get_object_or_404(InsuranceType, id=id)
    if request.method == 'POST':
        insurance_type.is_active = activate
        insurance_type.save()
    return redirect('pojistovna:insurance_list')


# Function to assign insurance to insured person.
def assign_insurance(request, id):
    insured_person = get_object_or_404(InsuredPerson, id=id)
    active_insurances = InsuranceType.objects.filter(is_active=True)

    
    insurance_subject = ''
    insurance_price = ''

    if request.method == 'POST':
        insurance_type_id = request.POST.get('insurance_type')
        insurance_subject = request.POST.get('insurance_subject')
        insurance_price_input = request.POST.get('insurance_price')
        
        try:
            insurance_price = Decimal(insurance_price_input)
        except (TypeError, InvalidOperation):
            messages.error(request, "Zadejte platnou cenu pojištění.")
    
        insurance_type = get_object_or_404(InsuranceType, id=insurance_type_id, is_active=True)  

        unique_number = str(uuid4())[:8]  # krátké unikátní číslo     

        # Vytvoření nového záznamu Insurance
        Insurance.objects.create(
            insured_person=insured_person,
            insurance_subject=insurance_subject,
            insurance_price=insurance_price,
            insurance_type=insurance_type,
            insurance_number=unique_number,

        )

        messages.success(request, "Pojištění bylo úspěšně vytvořeno a přiřazeno.")
        return redirect('pojistovna:insured_person_detail', id=id)

    return render(request, 'pojistovna/assign_insurance.html', {
        'insured_person': insured_person,
        'active_insurances': active_insurances,
        'insurance_subject': insurance_subject,
        'insurance_price':insurance_price,
    })


# Function to show insurance detail such as subject, price, etc.
def insurance_detail(request, id):    
    insurance = get_object_or_404(Insurance, id=id)
    events = Event.objects.filter(insurance=insurance)

    context = {
        'insurance': insurance,
        'events': events,
    }
    return render(request, 'pojistovna/insurance_detail.html', context)


# Function to edit insurance details such as subject, price, etc.
def edit_insurance(request, id):
    insurance = get_object_or_404(Insurance, pk=id)

    if request.method == 'POST':
        form = InsuranceForm(request.POST, instance=insurance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pojištění bylo úspěšně upraveno.')
            return redirect('pojistovna:insured_person_detail', id=insurance.insured_person.id)
        else:
            messages.error(request, 'Oprava se nezdařila. Zkontrolujte prosím formulář.')
    else:
        form = InsuranceForm(instance=insurance)

    return render(request, 'pojistovna/insurance_form.html', {'form': form, 'insurance': insurance})


# Function to remove insurance from database.
def insurance_delete(request, id):
    person = get_object_or_404(Insurance, pk=id)
    if request.method == "POST":
        person.delete()
        return redirect('pojistovna:insured_person') 


# Function to show a list of events in database ordered by date of create.
def event_list(request):
    all_events = Event.objects.all()
    paginator = Paginator(all_events, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,       
    }
    return render(request, 'pojistovna/event_list.html', context)


# Function to show event detail such as insurance or insured person name.
def event_detail(request, id):
    event = get_object_or_404(Event, id=id)

    context = {        
        'event': event,
    }

    return render(request, 'pojistovna/event_detail.html', context)


# Function to add event to insured person's insurance in database.
def add_event(request):
    if request.method == 'POST':
        form = AddEventForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Událost byla úspěšně přidána.")
            return redirect('pojistovna:event_list')
    else:
        form = AddEventForm()

    return render(request, 'pojistovna/add_event.html', {'form': form})



class InsuranceAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Insurance.objects.none()

        qs = Insurance.objects.select_related('insured_person', 'insurance_type')

        if self.q:
            qs = qs.filter(
                Q(insured_person__name__icontains=self.q) |
                Q(insured_person__surname__icontains=self.q)
            )
        return qs

    def get_result_label(self, result):
        return f"{result.insured_person.name} {result.insured_person.surname} – {result.insurance_type.insurance_name} ({result.insurance_number})"