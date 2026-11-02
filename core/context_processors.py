from .seo import (
    SITE_NAME,
    DEFAULT_DESCRIPTION,
    seo_context,
)


def seo_defaults(request):
    """
    اطلاعات عمومی SEO برای تمام قالب‌هایی که از RequestContext
    و base.html استفاده می‌کنند.
    """

    return seo_context(
        request,
        title=SITE_NAME,
        description=DEFAULT_DESCRIPTION,
        og_type="website",
        schema={
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": SITE_NAME,
            "description": DEFAULT_DESCRIPTION,
            "url": request.build_absolute_uri(request.path),
        },
    )
