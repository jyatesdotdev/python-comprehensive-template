FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Pin uv by image tag; do not curl|sh the installer (unpinned, harder to audit).
COPY --from=ghcr.io/astral-sh/uv:0.11.32 /uv /usr/local/bin/uv

# Copy the entrypoint outside /app so compose bind-mounts cannot hide it.
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY . .

# Runtime deps only (dev group holds test/lint/security tooling)
RUN uv sync --frozen --no-dev

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["fastapi", "run", "src/python_template/api/main.py", "--host", "0.0.0.0", "--port", "8000"]
