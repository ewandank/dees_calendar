FROM python:3.12-alpine
LABEL org.opencontainers.image.source=https://github.com/ewandank/dees_calendar
# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container. 
COPY . /app


WORKDIR /app
# Install deps.
RUN uv sync --frozen --no-cache

# Run PROD FastAPI.
EXPOSE 80
CMD ["/app/.venv/bin/fastapi", "run", "app/main.py", "--port", "80"]