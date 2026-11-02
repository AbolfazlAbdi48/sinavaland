import json

from django.core.exceptions import ValidationError
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

    articles = Article.objects.filter(is_published=True)[:3]

    accommodations = Accommodation.objects.all()[:3]

    estate = Estate.objects.filter(is_available=True)[:3]

    products = Product.objects.filter(
        is_available=True,
        stock__gt=0
    )[:3]

    accommodations_count = Accommodation.objects.count()
    estate_count = Estate.objects.count()
    products_count = Product.objects.count()

    return render(request, 'core/home.html', {
        "articles": articles,
        "accommodations": accommodations,
        "estate": estate,
        "products": products,
        "accommodations_count": accommodations_count,
        "estate_count": estate_count,
        "products_count": products_count,
    })


def contact(request):
    """تماس با ما"""
    if request.method == 'POST':
        name = request.POST.get('name')
        subject = request.POST.get('subject')
        contact_number = request.POST.get('contact_number')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        address = request.POST.get('address')

        phone_field = ContactMessage._meta.get_field('phone')
        contact_number_field = ContactMessage._meta.get_field('contact_number')

        try:
            phone_field.clean(phone, None)
            contact_number_field.clean(contact_number, None)
        except ValidationError as e:
            messages.error(request, e.messages[0])
            return redirect('core:contact')

        ContactMessage.objects.create(
            name=name,
            subject=subject,
            contact_number=contact_number,
            phone=phone,
            message=message,
            address=address,
        )
        messages.success(request, 'پیام شما با موفقیت ارسال شد.')
        return redirect('core:contact')

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
    return redirect('core:home', permanent=True)


def custom_404(request, exception):
    return render(request, '404.html', status=404)


def custom_500(request):
    return render(request, '500.html', status=500)


def robots_txt(request):
    content = """
User-agent: *

Disallow: /management-panel/
Disallow: /accounts/
Disallow: /cart/
Disallow: /ckeditor5/

Sitemap: https://sinavaland.ir/sitemap.xml
"""
    return HttpResponse(content, content_type="text/plain")
