from django.shortcuts import redirect
from django.urls.base import reverse_lazy, resolve

from src.age_verification.models import AgeVerificationCountry
from src.core.utils import get_ip_data


class AgeVerificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        # Exclude specific routes from age verification
        excluded_names = [
            'age_verification.country_restricted',
        ]
        resolver_match = resolve(request.path_info)
        if resolver_match.url_name in excluded_names:
            return self.get_response(request)

        ip_data = get_ip_data(None, request)
        if ip_data.is_usa():
            av_country = (
                AgeVerificationCountry.objects
                .filter(country_code=ip_data.country_code)
                .filter(state_code=ip_data.state_code)
                .filter(is_age_verification_required=True)
                .first()
            )
        else:
            av_country = (
                AgeVerificationCountry.objects
                .filter(country_code=ip_data.country_code)
                .filter(is_age_verification_required=True)
                .first()
            )

        if av_country:
            return redirect(reverse_lazy('age_verification.country_restricted'))

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
