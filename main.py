from ics import Calendar, Event
from ics.grammar.parse import ContentLine
import requests
from requests_cache import CachedSession
import arrow
from datetime import timedelta
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles

app = FastAPI(docs_url=None, redoc_url=None)

# Only supporting the Demons. This is a feature of this app.
team_id = 11

# Cache the requests to the squiggle api
session = CachedSession(
    "squiggle_cache", backend="sqlite", expire_after=timedelta(hours=8)
)

class CalendarResponse(Response):
    media_type = "text/calendar"

@app.get("/fixture.ics", response_class=CalendarResponse)
def get_calendar():
    c = Calendar(creator="Ewan Dank (github.com/ewandank)")
    c.extra.extend(
        [
            ContentLine(name="X-WR-CALNAME", value="Melbourne Demons"),
            ContentLine(name="NAME", value="Melbourne Demons"),
        ]
    )
    # get games from squiggle api.
    url = "https://api.squiggle.com.au/"
    # the current behaviour will load the new games on jan 1st.
    payload = {"q": "games", "year": arrow.now().format("YYYY"), "team": team_id}
    headers = {"User-Agent": "Demons Calendar - github.com/ewandank"}
    response = session.get(url, params=payload, headers=headers)
    games = response.json()["games"]
    for game in games:
        e = Event()
        if game["hteamid"] == team_id:
            e.name = f"{game['hteam']} vs {game['ateam']}"
        else:
            e.name = f"{game['ateam']} vs {game['hteam']}"
        e.location = game["venue"]
        e.begin = arrow.get(f"{game['date']}{game['tz']}")
        e.end = e.begin.shift(hours=+3)
        e.created = arrow.get(f"{game['updated']}{game['tz']}")
        e.uid = str(game["id"])

        c.events.add(e)
    return c.serialize()


# Serve the web directory on the `/` route.
# Serve static files from the `web` directory. This is intentionally after the endpoint or it encompasses it.
app.mount("/", StaticFiles(directory="web", html=True), name="web")
