from django.urls import path
from pojistovna.views import toggle_insurance_status, add_insurance, insurance_list, assign_insurance, insurance_detail, insurance_delete, insured_person_delete, dynamic_insured_person_search, InsuranceAutocomplete
from pojistovna.views import event_list, add_event, edit_insurance, event_detail, run_migrations
from pojistovna.views import home, users_list, user_delete, user_password_reset, dynamic_user_search, staff_and_super_list, add_super_user, add_staff_user, insured_person_register, insured_person_detail, login_view, logout_view, insured_person_list, add_insured_person, edit_insured_person
from django.contrib.auth import views as auth_views

app_name = 'pojistovna'

urlpatterns = [

    path('run-migrations/', run_migrations),

    path('', home, name='home'),  # URL pro domovskou stránku pojišťovny
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('insured_person/', insured_person_list, name='insured_person'),
    path('insured_person/<int:id>/register/', insured_person_register, name='register'),
    path('insured_person/add_insured_person/', add_insured_person, name='insured_person_form'),    
    path('insured_person/<int:id>/', insured_person_detail, name='insured_person_detail'),
    path('insured_person/<int:id>/edit/', edit_insured_person, name='edit_insured_person'),
    path("insured_person/search/", dynamic_insured_person_search, name="insured_person_search"),
    path('insured_person/<int:id>/delete/', insured_person_delete, name='insured_person_delete'),
    path('insured_person/<int:id>/assign_insurance', assign_insurance, name='assign_insurance'),

    path('insurance/', insurance_list, name='insurance_list'),
    path('insurance/add_insurance/', add_insurance, name='add_insurance'),
    path('insurance/<int:id>/activate/', toggle_insurance_status, {'activate': True}, name='activate_insurance'),
    path('insurance/<int:id>/deactivate/', toggle_insurance_status, {'activate': False}, name='deactivate_insurance'),
    path('insurance/<int:id>/', insurance_detail, name='insurance_detail'),
    path('insurance/<int:id>/edit/', edit_insurance, name='edit_insurance'),
    path('insurance/<int:id>/delete/', insurance_delete, name='insurance_delete'),    

    path('event/', event_list, name='event_list'),
    path('event/<int:id>/', event_detail, name='event_detail'),
    path('event/add_event/', add_event, name='add_event'),   
    path('event/autocomplete/', InsuranceAutocomplete.as_view(), name='insurance-autocomplete'),

    path('users/', users_list, name='users_list'),
    path('users/<int:id>/password_reset', user_password_reset, name='user_password_reset'),
    path('users/<int:id>/delete/', user_delete, name='user_delete'),
    path("users/search/", dynamic_user_search, name="user_search"),
    path('staff_and_super/', staff_and_super_list, name='staff_and_super_list'),
    path('staff_and_super/add_super', add_super_user, name='add_super_user'),
    path('staff_and_super/add_staff', add_staff_user, name='add_staff_user'),
    
]