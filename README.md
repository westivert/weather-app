# Väderapp
Ett eget projekt där jag övar på Python, Flask och API-anrop. Appen hämtar väderdata och visar resultatet på en webbsida.
## Funktioner
- Hämtar och bearbetar väderdata.
 Visar väderinformation i webbläsaren.
- Hanterar fel om data inte kan hämtas.

## Kom igång

Skapa och aktivera en virtuell miljö:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Installera paketen och starta appen:

```bash
pip install -r requirements.txt
python app.py
```
Öppna adressen som visas i terminalen.
## Tester och kodkontroll
```bash
pytest
ruff check .
```