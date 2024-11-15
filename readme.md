# Dees Calendar

A `FastAPI` application that that scrapes the [squiggle api](https://api.squiggle.com.au/) approximately every 8 hours for the Melbourne Demons and parses it into iCal Format.

## Build and Deployment

To Build this application, simply run the following docker command:

```bash
docker build . --tag=ghcr.io/ewandank/dees_calendar:latest
```

To push to the Github repository, login and run:

```bash
docker push ghcr.io/ewandank/dees_calendar:latest
```
