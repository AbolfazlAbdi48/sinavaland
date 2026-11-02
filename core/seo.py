import html
import json
import re
from decimal import Decimal

from django.conf import settings
from django.templatetags.static import static
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe

SITE_NAME = "سینوالند | سوئیس مازندران"

DEFAULT_DESCRIPTION = (
    "پلتفرم جامع سینوالند؛ اتصال تولیدکنندگان، "
    "تأمین‌کنندگان و خریداران"
)


def clean_description(value, limit=300):
    if not value:
        return ""

    # تبدیل HTML Entity به کاراکتر واقعی
    value = html.unescape(value)

    # تبدیل تگ‌های بلوکی به فاصله
    value = re.sub(
        r"</?(?:p|div|li|ul|ol|h[1-6]|br|blockquote)\b[^>]*>",
        " ",
        value,
        flags=re.IGNORECASE
    )

    # حذف سایر تگ‌های HTML
    value = strip_tags(value)

    # یکسان‌سازی فاصله‌ها
    value = value.replace("\xa0", " ")
    value = re.sub(r"\s+", " ", value).strip()

    # محدود کردن طول متن
    if len(value) > limit:
        value = value[:limit].rsplit(" ", 1)[0] + "..."

    return value


def absolute_image_url(request, image_field=None):
    """
    ساخت URL مطلق برای تصویر.
    در صورت نبود تصویر، لوگوی سایت برگردانده می‌شود.
    """
    if image_field:
        try:
            return request.build_absolute_uri(image_field.url)
        except (ValueError, AttributeError):
            pass

    return request.build_absolute_uri(static("slogo.png"))


def get_canonical_url(request):
    """
    ساخت Canonical URL.

    پارامترهای جستجو و فیلتر حذف می‌شوند.
    پارامتر page در صفحات صفحه‌بندی‌شده حفظ می‌شود.
    """
    canonical_path = request.path

    page = request.GET.get("page")

    # فقط وقتی page تنها پارامتر URL باشد آن را حفظ می‌کنیم.
    if page and page.isdigit() and int(page) > 1:
        if len(request.GET) == 1:
            canonical_path = f"{request.path}?page={page}"

    return request.build_absolute_uri(canonical_path)


def serialize_json_ld(data):
    """
    تبدیل داده Python به JSON امن برای قرار گرفتن در script.
    """
    serialized = json.dumps(
        data,
        ensure_ascii=False,
        separators=(",", ":"),
        default=str,
    )

    # جلوگیری از بسته شدن ناخواسته تگ script
    serialized = (
        serialized
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )

    return mark_safe(serialized)


def seo_context(
        request,
        *,
        title=None,
        description=None,
        image=None,
        schema=None,
        canonical_url=None,
        og_type="website",
):
    """
    ساخت Context مشترک SEO برای ویوها.
    """

    title = title or SITE_NAME
    description = clean_description(description)

    canonical_url = canonical_url or get_canonical_url(request)
    image_url = absolute_image_url(request, image)

    if schema is None:
        schema = {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": title,
            "url": canonical_url,
            "description": description,
        }

    return {
        "seo_title": title,
        "seo_description": description,
        "seo_image": image_url,
        "canonical_url": canonical_url,
        "seo_og_type": og_type,
        "seo_json_ld": serialize_json_ld(schema),
    }


def price_to_schema(price):
    """
    تبدیل قیمت تومان به ریال برای Schema.org.
    """
    multiplier = getattr(settings, "SEO_PRICE_MULTIPLIER", 10)

    return Decimal(str(price)) * Decimal(str(multiplier))


def product_offer(product, request):
    """
    ساخت Offer برای محصول.
    """

    price = price_to_schema(product.price)

    availability = (
        "https://schema.org/InStock"
        if product.is_available and product.stock > 0
        else "https://schema.org/OutOfStock"
    )

    return {
        "@type": "Offer",
        "url": request.build_absolute_uri(
            product.get_absolute_url()
        ),
        "price": format(price, "f"),
        "priceCurrency": settings.SEO_PRICE_CURRENCY,
        "availability": availability,
    }
