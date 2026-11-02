from django.urls import path
from . import views

app_name = 'estate'

urlpatterns = [
    # fixed paths must come BEFORE the <persian_slug:slug>/ catch-all
    path('<persian_slug:slug>/', views.estate_detail, name='detail'),
    path('', views.estate_list, name='list'),
]
