from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET


@require_GET
def country_restricted(request: HttpRequest) -> HttpResponse:
    return render(request, 'country_restricted.html')
