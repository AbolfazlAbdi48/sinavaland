from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('host/', views.host, name='host'),
    path('host/manifest.json', views.host_manifest, name='host_manifest'),
    path('host/sw.js', views.host_service_worker, name='host_service_worker'),
    path('tourist/', views.tourist, name='tourist'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
]
