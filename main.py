from ics import Calendar, Event
from ics.grammar.parse import ContentLine
from requests_cache import CachedSession
import arrow
from datetime import timedelta

app = FastAPI(docs_url=None, redoc_url=None)

# Only supporting the Demons. This is a feature of this app.
# Note that the mens and womens team id's are different.
TEAM_ID = 17
ROOT_URL = "https://aflapi.afl.com.au/afl/v2"

# Cache the requests
session = CachedSession(
    "afl_api_cache", backend="sqlite", expire_after=timedelta(hours=8)
)


class CalendarResponse(Response):
    media_type = "text/calendar"


def get_comp_ids():
    comps = session.get(f"{ROOT_URL}/competitions").json()["competitions"]
    ids = {}
    for comp in comps:
        if "AFL Premiership" in comp["name"]:
            ids["AFLM"] = comp["id"]
        elif "AFLW" in comp["name"]:
            ids["AFLW"] = comp["id"]
    return ids


def get_season_id(comp_id: int):
    seasons = session.get(
        f"{ROOT_URL}/competitions/{comp_id}/compseasons?pageSize=100"
    ).json()["compSeasons"]
    for season in seasons:
        # If we are in November, we likely want next years fixture, not this years one.
        today = arrow.now()
        year = (
            today.format("YYYY")
            if today.date().month < 11
            else today.shift(years=1).format("YYYY")
        )
        if str(year) in season["name"]:
            return season["id"]


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

    comps = get_comp_ids()
    comp_id = comps["AFLM"]
    season_id = get_season_id(comp_id)

    matches = session.get(
        f"{ROOT_URL}/matches",
        params={
            "competitionId": comp_id,
            "compSeasonId": season_id,
            # I think it only returns the number of games in a season anyway lol.
            "pageSize": 1000,
            "teamId": TEAM_ID,
        },
    ).json()["matches"]

    for match in matches:
        if match["status"] == "PLACEHOLDER":
            # If the time is undecided, don't put it in the calendar.
            continue

        e = Event()
        if match["home"]["team"]["id"] == TEAM_ID:
            # [team][name] changes during Doug Nicholls Round e.g from Melbourne to Naarm
            # Whilst not opposed to that it creates a lot of changes, and can't programatically only do it for the rounds I want to, without creating uneccessary updates.
            e.name = f"{match['home']['team']['club']['name']} vs {match['away']['team']['club']['name']}"
        else:
            e.name = f"{match['away']['team']['club']['name']} vs {match['home']['team']['club']['name']}"

        e.location = match["venue"]["name"]
        e.begin = arrow.get(match["utcStartTime"])
        e.end = e.begin.shift(hours=3)
        e.uid = str(match["id"])
        c.events.add(e)
    return c.serialize()


# Serve the web directory on the `/` route.
# This is intentionally after the endpoint or it tries to serve a file,
# rather then use the endpoint defined above.
app.mount("/", StaticFiles(directory="web", html=True), name="web")
