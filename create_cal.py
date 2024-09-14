from ics import Calendar, Event
from requests import get
import arrow
from ics.grammar.parse import ContentLine
import hashlib
import json
# Not supporting other teams, feature not a bug
c = Calendar(creator="Ewan Dank github.com/ewandank")
c.extra.extend([ContentLine(name="X-WR-CALNAME", value="Melbourne Demons"), ContentLine(name="NAME", value="Melbourne Demons")])

ROOT_URL = "https://aflapi.afl.com.au/afl/v2/"

def generate_id(game_id:int):
    '''
    the game ids are integers and im concerned they could collide. Hence i am adding some guff and md5 hashing it. 
    '''
    return hashlib.md5(f"{game_id}EWAN_GENERATED_CALENDAR".encode()).hexdigest()


# there's probably a nicer way to do this
def get_comp_ids():
    comps = get(f"{ROOT_URL}/competitions").json()["competitions"]
    ids = {}
    for comp in comps:
        if("AFL Premiership" in comp["name"]):
            ids["AFLM"] = comp["id"]
        elif("AFLW" in comp["name"]):
            ids["AFLW"] = comp["id"]
    return ids

def get_season_id(comp_id: int):
 seasons = get(f"{ROOT_URL}/competitions/{comp_id}/compseasons?pageSize=100").json()["compSeasons"]
 for season in seasons:
    if str(arrow.now().year) in season["name"]:
        return season["id"]
    
def get_fixtures(season_id: int, comp_id: int, team_id: int): 
    matches = get(f"{ROOT_URL}/matches", params={ "competitionId": comp_id, "compSeasonId": season_id, "pageSize": 1000,"teamId":team_id }).json()["matches"]
    for match in matches: 
        e =  Event()

        # Always have the format Melbourne vs "Other Team"
        if(match["home"]["team"]["id"] == team_id):
            e.name = f"{match["home"]["team"]["name"]} vs {match["away"]["team"]["name"]}"
        else: 
            e.name = f"{match["away"]["team"]["name"]} vs {match["home"]["team"]["name"]}"
        e.begin = arrow.get(match["utcStartTime"]).to("Australia/Melbourne")
        e.end = e.begin.shift(hours=3)
        e.uid = generate_id(match["id"])
        e.location = match["venue"]["name"]
        c.events.add(e)
        # if i wanted to set the last updated, i'd have to diff the values from the existing file. 




comps = get_comp_ids()
seasons = {"AFLW": get_season_id(comps["AFLW"]), "AFLM": get_season_id(comps["AFLM"])}
# I think the squiggle implementation is better for the mens. So i might do some custom stuff to pick an implementation. 
# get_fixtures(season_id=seasons["AFLM"], comp_id=comps["AFLM"], team_id=17)
get_fixtures(season_id=seasons["AFLW"], comp_id=comps["AFLW"], team_id=29)


# really need to make this better to test
with open("fixture.ics", "w") as f:
    f.writelines(c.serialize_iter())
    print("Written fixture to file successfully")