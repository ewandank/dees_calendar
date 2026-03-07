# Dees Calendar
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![GitHub branch check runs](https://img.shields.io/github/check-runs/ewandank/dees_calendar/main)
![GitHub last commit](https://img.shields.io/github/last-commit/ewandank/dees_calendar)

A `FastAPI` application that that scrapes the [squiggle api](https://api.squiggle.com.au/) approximately every 8 hours for the Melbourne Demons and parses it into iCal Format.

## Running Locally

This project is built with [`uv`](https://docs.astral.sh/uv/). The `FastAPI` Dev server can be run as follows:

```bash
uv run fastapi dev
```

`Ruff` is used for formatting and linting.

```bash
# To lint
ruff check
# To format 
ruff format
```

## Build and Deployment

To Build this application, simply run the following docker command:

```bash
docker build . --tag=ghcr.io/ewandank/dees_calendar:latest
```

To push to the Github repository, login and run:

```bash
docker push ghcr.io/ewandank/dees_calendar:latest
```
