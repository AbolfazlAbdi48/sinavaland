from django.urls import path
from . import views

app_name = 'estate'

urlpatterns = [
    # fixed paths must come BEFORE the <persian_slug:slug>/ catch-all
    path('my/reservations/', views.my_reservations, name='my_reservations'),
    path('<persian_slug:slug>/', views.estate_detail, name='detail'),
    path('', views.estate_list, name='list'),
    path('<persian_slug:slug>/reserve/', views.reserve_estate, name='reserve'),
    path('<persian_slug:slug>/cancel/', views.cancel_reservation, name='cancel_reservation'),
]
