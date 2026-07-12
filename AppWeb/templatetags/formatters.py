from django import template

register = template.Library()


@register.filter
def format_decimal(value, decimals=4):
    try:
        return f"{float(value):.{decimals}f}"
    except (ValueError, TypeError):
        return value


@register.filter
def format_currency(value):
    try:
        value = float(value)
        formatted = f"{value:,.2f}"
        int_part, dec_part = formatted.split(".")
        int_part = int_part.replace(",", ".")
        return f"${int_part},{dec_part}"
    except (ValueError, TypeError):
        return value


@register.filter
def format_ratio(value):
    try:
        return f"{float(value):.2f}x"
    except (ValueError, TypeError):
        return value


@register.filter
def format_pct(value):
    try:
        return f"{float(value) * 100:.2f}%"
    except (ValueError, TypeError):
        return value
