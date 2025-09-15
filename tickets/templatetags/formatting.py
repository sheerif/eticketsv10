from django import template
register = template.Library()

@register.filter
def shortkey(value, keep=8):
    try:
        keep = int(keep)
    except Exception:
        keep = 8
    v = str(value)
    if len(v) <= keep*2+1:
        return v
    return f"{v[:keep]}…{v[-keep:]}"
