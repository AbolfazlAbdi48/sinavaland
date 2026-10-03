import json
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ContactMessage

from magazine.models import Article
from accommodations.models import Accommodation
from estate.models import Estate
from marketplace.models import Product


def home(request):
    """صفحه اصلی"""

    articles = Article.objects.all()[:3]
    accommodations = Accommodation.objects.all()[:3]
    estate = Estate.objects.all()[:3]
    products = Product.objects.all()[:3]

    return render(request, 'core/home.html', {
        "articles": articles,
        "accommodations": accommodations,
        "estate": estate,
        "products": products
    })


def contact(request):
    """تماس با ما"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        ContactMessage.objects.create(
            name=name,
            email=email,
            phone=phone,
            message=message
        )
        messages.success(request, 'پیام شما با موفقیت ارسال شد.')
        return redirect('contact')

    return render(request, 'core/contact.html')


def host(request):
    return render(request, 'core/host.html')


def host_manifest(request):
    manifest = {
        "name": "سینوالند | نسخه میزبانی",
        "short_name": "سینوالند Host",
        "description": "نسخه مخصوص این صفحه برای نصب سریع و جداگانه",
        "start_url": "/host/",
        "scope": "/host/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#1a2744",
        "orientation": "any",
        "icons": [
            {
                "src": "/static/slogo.png",
                "sizes": "160x160",
                "type": "image/png"
            }
        ]
    }
    return HttpResponse(json.dumps(manifest), content_type='application/manifest+json')


def host_service_worker(request):
    sw = """
    const CACHE_NAME = 'sinavaland-host-v1';
    const OFFLINE_URLS = ['/host/'];

    self.addEventListener('install', event => {
        event.waitUntil(
            caches.open(CACHE_NAME).then(cache => cache.addAll(OFFLINE_URLS))
        );
        self.skipWaiting();
    });

    self.addEventListener('activate', event => {
        event.waitUntil(self.clients.claim());
    });

    self.addEventListener('fetch', event => {
        if (event.request.mode === 'navigate') {
            event.respondWith(
                fetch(event.request).catch(() => caches.match('/host/'))
            );
        }
    });
    """
    return HttpResponse(sw, content_type='application/javascript')


def tourist(request):
    return render(request, 'core/home.html')
