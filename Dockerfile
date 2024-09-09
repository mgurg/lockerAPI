FROM python:3.12-slim-bullseye

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

WORKDIR /src

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
ENV UV_PYTHON_PREFERENCE=only-system

COPY --chown=appuser:appuser pyproject.toml .
COPY --chown=appuser:appuser uv.lock .

RUN uv sync --frozen --no-cache

USER appuser

# Install the application dependencies.
COPY --chown=appuser:appuser ./app /src/app
COPY --chown=appuser:appuser ./migrations /src/migrations
COPY --chown=appuser:appuser ./alembic.ini /src/alembic.ini

EXPOSE 5000

#CMD ["uvicorn", "app.main:app","--no-server-header","--no-proxy-headers", "--host", "0.0.0.0", "--port", "5000" ]

# Run the application.
CMD ["/src/.venv/bin/fastapi", "run", "/src/app/main.py", "--port", "5000"]

