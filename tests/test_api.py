from copy import deepcopy
from unittest.mock import patch

import pytest
import requests

from api import VaderFel, data_temp
from app import app
from vader import DataFel, bearbeta_data

DATA = {
    "current": {
        "temperature_2m": 4.5,
        "wind_speed_10m": 12.0,
    },
    "daily": {
        "time": ["2026-11-07", "2026-11-08", "2026-11-09"],
        "temperature_2m_max": [6, 9, 3],
        "temperature_2m_min": [1, 2, -2],
        "precipitation_sum": [0, 2.5, 1],
    },
}


@pytest.fixture
def client():
    app.config.update(TESTING=True)

    with app.test_client() as client:
        yield client


@pytest.mark.parametrize("temp", [4.5, 0, -10])
def test_bearbeta_data(temp):
    data = deepcopy(DATA)
    data["current"]["temperature_2m"] = temp

    resultat = bearbeta_data(data)

    assert resultat["temperatur"] == temp
    assert resultat["vind"] == 12
    assert len(resultat["dagar"]) == 3
    assert resultat["dagar"][0] == {
        "datum": "2026-11-07",
        "hogsta": 6,
        "lagsta": 1,
        "nederbord": 0,
    }


def test_api():
    with patch("api.requests.get") as mock_get:
        mock_get.return_value.json.return_value = DATA

        assert data_temp("Stockholm") == DATA

        mock_get.assert_called_once()
        mock_get.return_value.raise_for_status.assert_called_once()

        params = mock_get.call_args.kwargs["params"]

        assert params["latitude"] == 59.33
        assert params["longitude"] == 18.07
        assert params["forecast_days"] == 3
        assert params["timezone"] == "auto"
        assert mock_get.call_args.kwargs["timeout"] == 10


def test_timeout(client):
    with patch("api.requests.get") as mock_get:
        mock_get.side_effect = requests.Timeout()

        with pytest.raises(VaderFel):
            data_temp("Stockholm")

        svar = client.get("/prognos?stad=Stockholm")

        assert svar.status_code == 503
        assert "Försök igen" in svar.text
        assert client.get("/").status_code == 200


def test_http_fel(client):
    with patch("api.requests.get") as mock_get:
        mock_get.return_value.raise_for_status.side_effect = requests.HTTPError()

        with pytest.raises(VaderFel):
            data_temp("Stockholm")

        svar = client.get("/prognos?stad=Stockholm")

        assert svar.status_code == 503
        assert "kunde inte nås" in svar.text
        mock_get.return_value.json.assert_not_called()


def test_startsida(client):
    with patch("api.requests.get") as mock_get:
        svar = client.get("/")

        assert svar.status_code == 200
        assert 'name="stad"' in svar.text

        for stad in ["Stockholm", "Göteborg", "Malmö", "Umeå", "Kiruna"]:
            assert f'value="{stad}"' in svar.text

        mock_get.assert_not_called()


def test_prognos(client):
    with patch("api.requests.get") as mock_get:
        mock_get.return_value.json.return_value = DATA

        svar = client.get("/prognos?stad=Stockholm")

        assert svar.status_code == 200
        assert "Stockholm" in svar.text
        assert "4,5 °C" in svar.text
        assert "12.0" in svar.text
        assert "km/h" in svar.text

        for datum in DATA["daily"]["time"]:
            assert datum in svar.text

        # Medel av högsta temperaturerna: (6 + 9 + 3) / 3.
        assert "6,0 °C" in svar.text
        assert "Medel av tre dagars högsta" in svar.text
        assert "Plotly.newPlot" in svar.text


def test_fel_stad(client):
    with patch("api.requests.get") as mock_get:
        svar = client.get("/prognos")

        assert svar.status_code == 400
        assert "Välj en stad" in svar.text

        svar = client.get("/prognos?stad=London")

        assert svar.status_code == 404
        assert "Staden finns inte" in svar.text
        assert "FEL 404" in svar.text

        svar = client.get("/finns-inte")

        assert svar.status_code == 404
        assert "FEL 404" in svar.text
        mock_get.assert_not_called()


def test_saknad_data(client):
    data = deepcopy(DATA)
    del data["daily"]["temperature_2m_max"]

    with pytest.raises(DataFel):
        bearbeta_data(data)

    with patch("api.requests.get") as mock_get:
        mock_get.return_value.json.return_value = data

        svar = client.get("/prognos?stad=Stockholm")

        assert svar.status_code == 502
        assert "ofullständiga" in svar.text
