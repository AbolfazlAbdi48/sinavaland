import jdatetime
from django import template

register = template.Library()


@register.filter
def to_jalali(value, show_time=False):
    if not value:
        return ""

    if hasattr(value, "date"):
        date_value = value.date()
        time_value = value.time()
    else:
        date_value = value
        time_value = None

    jalali = jdatetime.date.fromgregorian(date=date_value)

    result = jalali.strftime("%Y/%m/%d")

    if show_time and time_value:
        result += f" {time_value.strftime('%H:%M')}"

    return result
