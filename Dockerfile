# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    uv pip install --system -r requirements.txt

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY /app .

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

CMD ["fastapi", "dev", "main.py", "--reload", "--port", "8000", "--host", "0.0.0.0"]