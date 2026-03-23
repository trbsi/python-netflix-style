import csv

from automationapp import settings
from src.age_verification.models import AgeVerificationCountry


class AgeVerificationSeeder:
    @staticmethod
    def seed():
        countries = f"{settings.BASE_DIR}/database/seeders/data/all_countries_iso.csv"
        states = f"{settings.BASE_DIR}/database/seeders/data/us_states_iso.csv"

        i = 0
        with open(countries, mode='r') as file:
            csvFile = csv.reader(file)
            for lines in csvFile:
                if i == 0:
                    i = i + 1
                    continue

                AgeVerificationCountry.objects.create(
                    country_code=lines[1],
                    country_name=lines[0],
                    is_age_verification_required=bool(int(lines[2])),
                )

        i = 0
        with open(states, mode='r') as file:
            csvFile = csv.reader(file)
            for lines in csvFile:
                if i == 0:
                    i = i + 1
                    continue

                AgeVerificationCountry.objects.create(
                    country_code='US',
                    country_name='United States',
                    state_name=lines[0],
                    state_code=lines[1],
                    is_age_verification_required=bool(int(lines[2])),
                )
