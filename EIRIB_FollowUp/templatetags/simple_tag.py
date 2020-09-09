from django import template
from EIRIB_FollowUp import utils
from EIRIB_FollowUpProject import settings

register = template.Library()


@register.simple_tag()
def version():
    return settings.VERSION


@register.simple_tag()
def admin_tel():
    return settings.ADMIN_TEL


@register.simple_tag()
def admin_email():
    return settings.ADMIN_EMAIL


@register.simple_tag()
def data_loading():
    return utils.data_loading()


@register.simple_tag()
def navigation_counter(request, pk):
    return {'item': request.session['enactment_query_set'].index({'pk': pk}) + 1,
            'items': len(request.session['enactment_query_set']),
            'filtered': request.session['filtered_enactment_query_set']}
