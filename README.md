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

1. Why do you mock the API calls in your tests, and what would happen if you didn’t?
I mock the API calls so I can test my code without internet and control what data the tests receive. In tests/test_api.py, I use patch("api.requests.get") and set the mocked call to return my test data, DATA. Without mocking, a test could fail because the network or API is down, even if my code is correct. I also use mocking to simulate timeouts and HTTP errors to check how the app handles them.

2. What do timeout and raise_for_status() do, and why are they necessary?
In api.py, I use timeout=10 so the call does not wait indefinitely for a connection or for more data to arrive. This does not mean the whole request will always finish within ten seconds. raise_for_status() raises HTTPError if the response has an HTTP error code, such as 404 or 500. I catch these errors through requests.RequestException and convert them into VaderFel so the app can show a clear message to the user.

3. How does template inheritance work in Jinja2? Explain using examples from your own templates.
Template inheritance means other pages can use a base template, so I do not need to repeat the same HTML. My base.html contains the CSS, header, footer and the blocks titel and innehall. My prognos.html uses {% extends "base.html" %} and fills these blocks with its own title and weather information. If I want to change something shared by the pages, I can change it in base.html.

4. What is a fixture, and which one do you use?
A fixture prepares something a test needs, so I do not have to repeat the same setup in several tests. I use the client fixture in tests/test_api.py, where @pytest.fixture marks the fixture, TESTING is enabled and app.test_client() creates a test client. Tests receive it by including client as an argument, allowing them to test routes without starting a real web server. yield gives the client to the test, and after the test finishes, the with block exits and cleans up the client context.
#€cheboy€#
