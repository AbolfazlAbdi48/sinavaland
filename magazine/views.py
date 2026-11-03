from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Article

from core.seo import (
    seo_context,
    clean_description,
)


def article_list(request):
    """لیست مقالات منتشرشده"""

    articles = (
        Article.objects
        .filter(is_published=True)
        .select_related("author")
    )

    # فیلتر دسته‌بندی
    category = request.GET.get("category", "").strip()

    valid_categories = dict(Article.CATEGORY_CHOICES)

    if category in valid_categories:
        articles = articles.filter(category=category)
    else:
        category = ""

    # جستجو
    search = request.GET.get("search", "").strip()

    if search:
        articles = articles.filter(
            Q(title__icontains=search) |
            Q(content__icontains=search)
        )

    # مرتب‌سازی و صفحه‌بندی
    articles = articles.order_by("-created_at")

    paginator = Paginator(articles, 12)
    articles = paginator.get_page(request.GET.get("page"))

    # Canonical
    canonical_url = request.build_absolute_uri(request.path)

    if articles.number > 1:
        canonical_url = f"{canonical_url}?page={articles.number}"

    context = {
        "articles": articles,
        "categories": Article.CATEGORY_CHOICES,
        "selected_category": category,
        "search_query": search,
    }

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

    return render(request, "magazine/list.html", context)


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
