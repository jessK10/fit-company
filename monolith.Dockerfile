# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./

COPY main_monolith.py /app/main_monolith.py

RUN uv sync

ENV FLASK_ENV=development
ENV PYTHONPATH=/app/src


EXPOSE 5000

CMD ["uv", "run", "main_monolith.py"] 