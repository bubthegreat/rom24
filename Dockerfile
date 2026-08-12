FROM python:3.12-slim

# Runtime certs (uv fetches deps over TLS).
RUN apt-get -y update && \
    apt-get -y install --no-install-recommends ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install the UV package manager.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /pyrom

# Project metadata + source. ./src carries the game data too
# (src/packs/**, src/areas/**, src/data/**), which the server reads at runtime.
COPY ./pyproject.toml /pyrom/pyproject.toml
COPY ./README.md /pyrom/README.md
COPY ./src /pyrom/src

# Editable install: pulls runtime deps (jsonschema, psutil) and installs the
# rom24 package in place, so settings.py resolves INSTALLED_DIR=/pyrom and finds
# /pyrom/src/{packs,areas,data}. (A non-editable wheel would drop the data.)
RUN uv pip install --system -e .

# Persistent-storage mount points (player saves, world, system state).
RUN mkdir -p /pyrom-persistent/players \
    /pyrom-persistent/world \
    /pyrom-persistent/system

# Telnet port.
EXPOSE 1337

# The port speaks telnet, not HTTP — probe it with a raw TCP connect.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import socket; socket.create_connection(('127.0.0.1', 1337), 3).close()" || exit 1

# Run the MUD server (console script from pyproject: rom24 = rom24.pyom:pyom).
CMD ["rom24"]
