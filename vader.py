from datetime import date
from math import isfinite

import pandas as pd
import plotly.express as px

STADER = {
    "Stockholm": (59.33, 18.07),
    "Göteborg": (57.71, 11.97),
    "Malmö": (55.61, 13.00),
    "Umeå": (63.83, 20.26),
    "Kiruna": (67.86, 20.23),
}


class DataFel(ValueError):
    """Fel när väderdata saknas eller innehåller ogiltiga värden."""


def giltig_stad(stad):
    return isinstance(stad, str) and stad in STADER


def kontrollera_tal(varde):
    # Saknade värden och bool ska inte räknas som temperaturer.
    if isinstance(varde, bool) or not isinstance(varde, (int, float)):
        raise DataFel("Väderdata innehåller ett saknat eller ogiltigt mätvärde.")

    if not isfinite(varde):
        raise DataFel("Väderdata innehåller ett ogiltigt mätvärde.")

    return varde


def bearbeta_data(data):
    try:
        nu = data["current"]

        temperatur = kontrollera_tal(nu["temperature_2m"])
        vind = kontrollera_tal(nu["wind_speed_10m"])

        if vind < 0:
            raise DataFel("Vindhastigheten kan inte vara negativ.")

        daily = data["daily"]

        nycklar = (
            "time",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
        )

        listor = [daily[nyckel] for nyckel in nycklar]

        # Alla listor måste innehålla tre dagar.
        if any(not isinstance(lista, list) or len(lista) != 3 for lista in listor):
            raise DataFel("Prognosen måste innehålla tre kompletta dagar.")

        dagar = []

        # Koppla ihop datum och mätvärden från samma position.
        for datum, hogsta, lagsta, regn in zip(*listor):  # noqa: B905
            datum = date.fromisoformat(datum)

            hogsta = kontrollera_tal(hogsta)
            lagsta = kontrollera_tal(lagsta)
            regn = kontrollera_tal(regn)

            if hogsta < lagsta or regn < 0:
                raise DataFel("Prognosen innehåller orimliga värden.")

            dagar.append(
                {
                    "datum": datum.isoformat(),
                    "hogsta": hogsta,
                    "lagsta": lagsta,
                    "nederbord": regn,
                }
            )

        datumlista = [dag["datum"] for dag in dagar]

        if datumlista != sorted(set(datumlista)):
            raise DataFel("Prognosens datum är inte unika och sorterade.")

        forsta = date.fromisoformat(datumlista[0])
        sista = date.fromisoformat(datumlista[-1])

        if (sista - forsta).days != 2:
            raise DataFel("Prognosens dagar måste följa på varandra.")

        return {
            "temperatur": temperatur,
            "vind": vind,
            "dagar": dagar,
        }

    except (KeyError, TypeError, ValueError, OverflowError) as fel:
        if isinstance(fel, DataFel):
            raise

        raise DataFel("Vädertjänsten skickade ofullständiga eller felaktiga data.") from fel


def formatera_temperatur(varde):
    return f"{kontrollera_tal(varde):.1f}".replace(".", ",") + " °C"


def sammanfatta(dagar):
    # Skapa en DataFrame och beräkna medel av högsta temperaturerna.
    df = pd.DataFrame(dagar)
    medel = float(df["hogsta"].mean())

    figur = px.line(
        df,
        x="datum",
        y=["hogsta", "lagsta"],
        markers=True,
        labels={
            "datum": "Datum",
            "value": "Temperatur (°C)",
            "variable": "Temperatur",
        },
        color_discrete_sequence=["#b8542c", "#246a85"],
    )

    # Ge kurvorna svenska namn.
    for kurva in figur.data:
        if kurva.name == "hogsta":
            kurva.name = "Högsta"
        else:
            kurva.name = "Lägsta"

    figur.update_layout(
        template="plotly_white",
        height=340,
        margin=dict(l=35, r=20, t=20, b=40),
        legend_title_text="",
        font=dict(family="Arial"),
    )

    figur.update_xaxes(type="category")

    return medel, figur


def diagram_html(figur):
    # Gör om diagrammet till HTML för Jinja-mallen.
    return figur.to_html(
        full_html=False,
        include_plotlyjs=True,
        config={
            "responsive": True,
            "displayModeBar": False,
        },
    )
