from ics import Calendar, Event
import requests
import arrow
from os import environ
from ics.grammar.parse import ContentLine
from fastapi import FastAPI

app = FastAPI()

# Not supporting other teams, feature not a bug
# Constants??
team_id = 11
c = Calendar(creator="Ewan Dank github.com/ewandank")
c.extra.extend([ContentLine(name="X-WR-CALNAME", value="Melbourne Demons"), ContentLine(name="NAME", value="Melbourne Demons")])


def write_cal():
    # get games from squiggle api
    url = "https://api.squiggle.com.au/?q=games"
    payload = {"year": arrow.now().format("YYYY"), "team": team_id}
    headers = {"User-Agent": environ["EMAIL"], "From": environ["NAME"]}
    response = requests.get(url, params=payload, headers=headers)
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
    # really need to make this better to test
    with open("/usr/share/nginx/html/fixture.ics", "w") as f:
        f.writelines(c.serialize_iter())
        print("Written fixture to file successfully")


@app.get("/")
def read_root():
    return {"Hello": "World"}