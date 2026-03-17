class IpData:
    def __init__(self, timezone=None, country_code=None, state_code=None):
        self.timezone = timezone
        self.country_code = country_code
        self.state_code = state_code

    def is_usa(self) -> bool:
        return self.country_code == 'US'
