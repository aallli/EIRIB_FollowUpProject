from django.shortcuts import redirect
from .utils import update_data


def update_data_view(request):
    update_data()
    return redirect(request.META['HTTP_REFERER'])
