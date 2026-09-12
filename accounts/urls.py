from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('compelete_profile/', views.complete_profile, name='complete-profile'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('request-otp/', views.request_otp, name='request-otp')
]
