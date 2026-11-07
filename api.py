import requests

from vader import STADER, giltig_stad

URL = "https://api.open-meteo.com/v1/forecast"


class VaderFel(Exception):
    """Fel när vädertjänsten inte kan ge ett läsbart svar."""


def data_temp(stad):
    # Välj koordinater för staden.
    if not giltig_stad(stad):
        raise ValueError("Staden finns inte i listan.")

    latitud, longitud = STADER[stad]

    params = {
        "latitude": latitud,
        "longitude": longitud,
        "current": "temperature_2m,wind_speed_10m",
        "daily": ("temperature_2m_max,temperature_2m_min,precipitation_sum"),
        "timezone": "auto",
        "forecast_days": 3,
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm",
    }

    try:
        svar = requests.get(URL, params=params, timeout=10)
        svar.raise_for_status()

        return svar.json()

    except requests.RequestException as fel:
        raise VaderFel("Vädertjänsten kunde inte nås. Försök igen om en stund.") from fel

    except ValueError as fel:
        raise VaderFel("Vädertjänsten skickade ett oläsbart svar.") from fel
