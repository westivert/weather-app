import pandas as pd
import plotly.express as px
from flask import Flask, abort, render_template, request

from api import VaderFel, data_temp
from vader import STADER, DataFel, bearbeta_data, formatera_temperatur

app = Flask(__name__)
app.add_template_filter(formatera_temperatur, "temperatur")


@app.route("/")
def home():
    return render_template("index.html", stader=STADER)


@app.route("/prognos")
def sokningen():
    stad = request.args.get("stad", "").strip()

    if not stad:
        return render_template(
            "fel.html",
            kod=400,
            meddelande="Välj en stad först.",
        ), 400

    if stad not in STADER:
        abort(404, description="Staden finns inte i listan.")

    try:
        data = data_temp(stad)

        vader = bearbeta_data(data)
        df = pd.DataFrame(vader["dagar"])

        medel = float(df["hogsta"].mean())

        linje = px.line(
            df,
            x="datum",
            y=["hogsta", "lagsta"],
            markers=True,
            title=f"Temperatur de kommande tre dagarna – {stad}",
            labels={
                "datum": "Datum",
                "value": "Temperatur (°C)",
                "variable": "Temperatur",
            },
        )

        linje.update_xaxes(type="category")

    except VaderFel as fel:
        print("API-fel:", repr(fel))

        return render_template(
            "fel.html",
            kod=503,
            meddelande=str(fel),
        ), 503

    except DataFel as fel:
        print("Data-fel:", repr(fel))

        return render_template(
            "fel.html",
            kod=502,
            meddelande=str(fel),
        ), 502

    return render_template(
        "prognos.html",
        stad=stad,
        vader=vader,
        medel=medel,
        diagram=linje.to_html(
            full_html=False,
            include_plotlyjs=True,
        ),
    )


@app.errorhandler(404)
def hittades_inte(fel):
    return render_template(
        "fel.html",
        kod=404,
        meddelande=fel.description,
    ), 404


if __name__ == "__main__":
    app.run(debug=True)