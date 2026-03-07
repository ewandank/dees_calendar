from ics import Calendar, Event
from ics.grammar.parse import ContentLine
from requests_cache import CachedSession
import arrow
from datetime import timedelta
from fastapi import FastAPI, Response
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
            # Refresh Every 4 hours, As the cache could have changed.
            ContentLine(name="REFRESH-INTERVAL;VALUE=DURATION", value="PT4H"),
            ContentLine(name="X-PUBLISHED-TTL", value="14400"),
        ]
    )
    # get games from squiggle api.
    url = "https://api.squiggle.com.au/"

    today = arrow.now()

    # If we are in november, we likely want next years fixture, not this years one.
    year = (
        today.format("YYYY")
        if today.date().month < 11
        else today.shift(years=1).format("YYYY")
    )

    # See https://api.squiggle.com.au/#section_bots
    headers = {
        "User-Agent": "Demons Calendar - https://github.com/ewandank/dees_calendar"
    }

    response = session.get(
        url, params={"q": "games", "year": year, "team": team_id}, headers=headers
    )
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
# This is intentionally after the endpoint or it tries to serve a file,
# rather then use the endpoint defined above.
app.mount("/", StaticFiles(directory="web", html=True), name="web")
