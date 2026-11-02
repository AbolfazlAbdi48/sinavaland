from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator

from .models import Article

from core.seo import (
    seo_context,
    clean_description,
)


def article_list(request):
    """لیست مقالات"""

    articles = Article.objects.filter(
        is_published=True
    ).order_by("-created_at")

    # فیلتر بر اساس دسته‌بندی
    category = request.GET.get("category")

    if category:
        articles = articles.filter(category=category)

    # جستجو
    search = request.GET.get("search")

    if search:
        articles = (
                articles.filter(title__icontains=search)
                | articles.filter(content__icontains=search)
        )

    # صفحه‌بندی
    paginator = Paginator(articles, 12)
    page_number = request.GET.get("page")
    articles = paginator.get_page(page_number)

    context = {
        "articles": articles,
        "categories": Article.CATEGORY_CHOICES,
    }

    # Canonical
    canonical_url = request.build_absolute_uri(request.path)

    if articles.number > 1:
        canonical_url = f"{canonical_url}?page={articles.number}"

    context.update(
        seo_context(
            request,
            title="مجله سینوالند | سفر، فرهنگ و طبیعت مازندران",
            description=(
                "مقالات و مطالب گردشگری، سفر، فرهنگ، غذا و طبیعت "
                "مازندران را در مجله سینوالند بخوانید."
            ),
            canonical_url=canonical_url,
            schema={
                "@context": "https://schema.org",
                "@type": "CollectionPage",
                "name": "مجله سینوالند",
                "description": (
                    "مقالات گردشگری، فرهنگ، غذا و طبیعت مازندران."
                ),
                "url": canonical_url,
            },
        )
    )

    return render(
        request,
        "magazine/list.html",
        context,
    )


def article_detail(request, slug):
    """جزئیات مقاله"""

    article = get_object_or_404(
        Article,
        slug=slug,
        is_published=True,
    )

    # URL اصلی مقاله
    article_url = request.build_absolute_uri(
        article.get_absolute_url()
    )

    # توضیحات پاک‌سازی‌شده
    description = clean_description(
        article.excerpt or article.content
    )

    # تصویر مقاله
    images = []

    if article.image:
        images.append(
            request.build_absolute_uri(article.image.url)
        )

    # Schema
    schema = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "@id": f"{article_url}#article",
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": article_url,
        },
        "headline": article.title,
        "description": description,
        "articleSection": article.get_category_display(),
        "datePublished": article.created_at.isoformat(),
        "dateModified": article.updated_at.isoformat(),
        "author": {
            "@type": "Person",
            "name": f"{str(article.author.first_name)} {str(article.author.last_name)}",
        },
        "publisher": {
            "@type": "Organization",
            "name": "سینوالند",
        },
    }

    if images:
        schema["image"] = images

    context = {
        "article": article,
    }

    context.update(
        seo_context(
            request,
            title=f"{article.title} | مجله سینوالند",
            description=description,
            image=article.image,
            schema=schema,
            canonical_url=article_url,
            og_type="article",
        )
    )

    return render(
        request,
        "magazine/detail.html",
        context,
    )
