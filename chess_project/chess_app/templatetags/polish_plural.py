from django import template

register = template.Library()

@register.filter
def zadania(count):
    count = int(count)

    if count == 1:
        return "zadanie"
    if 2 <= count % 10 <= 4 and not (12 <= count % 100 <= 14):
        return "zadania"
    return "zadań"
