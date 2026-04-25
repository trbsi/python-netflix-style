from django.utils.text import slugify


class IpData:
    def __init__(self, timezone=None, country_code=None, state_code=None, state_name=None):
        self.timezone = timezone
        self.country_code = country_code
        self.state_code = state_code
        self.state_name = slugify(state_name)

    def is_usa(self) -> bool:
        return self.country_code == 'US'



    def get_language(self) -> str:
        if not self.country_code:
            return 'en'

        balkan_countries = {
            'BA',  # Bosnia and Herzegovina
            'HR',  # Croatia
            'ME',  # Montenegro
            'RS',  # Serbia
            'SI',  # Slovenia
            'MK',  # North Macedonia
            'XK',  # Kosovo
        }

        spanish_speaking = {
            'ES',  # Spain
            'MX',  # Mexico
            'AR',  # Argentina
            'CO',  # Colombia
            'PE',  # Peru
            'VE',  # Venezuela
            'CL',  # Chile
            'EC',  # Ecuador
            'GT',  # Guatemala
            'CU',  # Cuba
            'BO',  # Bolivia
            'DO',  # Dominican Republic
            'HN',  # Honduras
            'PY',  # Paraguay
            'SV',  # El Salvador
            'NI',  # Nicaragua
            'CR',  # Costa Rica
            'PA'   # Panama
        }

        german_speaking = {
            'DE',  # Germany
            'AT',  # Austria
            'CH',  # Switzerland
            'LI',  # Liechtenstein
            'LU'   # Luxembourg (partially German-speaking)
        }

        if self.country_code in balkan_countries:
            return 'hr'

        if self.country_code in spanish_speaking:
            return 'es'

        if self.country_code in german_speaking:
            return 'de'

        return 'en'