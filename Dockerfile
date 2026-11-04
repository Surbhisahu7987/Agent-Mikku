# syntax=docker/dockerfile:1

# ==============================================================================
# Stage 1: Dependency Installation Stage
# Uses Astral's official uv image with Python 3.13 pre-installed
# ==============================================================================
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

WORKDIR /app

# Enable bytecode compilation and use copy mode for linking
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Copy dependency definitions first to maximize Docker layer caching
COPY pyproject.toml uv.lock README.md ./

# Install dependencies into virtual environment (.venv) using uv sync
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# ==============================================================================
# Stage 2: Runtime Stage
# Lean Python 3.13 Debian Bookworm slim runtime
# ==============================================================================
FROM python:3.13-slim-bookworm AS runtime

WORKDIR /app

# Ensure stdout/stderr output is sent directly to terminal and disable pyc caching at runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Copy installed dependencies from builder's site-packages to system site-packages
COPY --from=builder /app/.venv/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/

# Copy the application source files into the container
COPY . /app

# Run the CLI application
CMD ["python", "main.py"]

