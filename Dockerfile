FROM python:3.14-alpine
LABEL org.opencontainers.image.source=https://github.com/ewandank/dees_calendar
# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container. 
COPY . /app


WORKDIR /app
# Install build deps needed to compile packages without pre-built wheels for Python 3.14,
# then remove them to keep the image small.
RUN apk add --no-cache --virtual .build-deps gcc musl-dev \
    && uv sync --frozen --no-cache \
    && apk del .build-deps

# Run PROD FastAPI.
EXPOSE 80
CMD ["/app/.venv/bin/fastapi", "run", "main.py", "--port", "80"]