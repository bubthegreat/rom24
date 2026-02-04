FROM python:3.12-slim

# Install required packages
RUN apt-get -y update && \
    apt-get -y install --no-install-recommends \
        curl \
        ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install UV package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV PATH="/root/.cargo/bin:${PATH}"

# Set working directory
WORKDIR /pyrom

# Copy source code and data
COPY ./src /pyrom/src
COPY ./requirements.txt /pyrom/requirements.txt
COPY ./setup.py /pyrom/setup.py
COPY ./MANIFEST.in /pyrom/MANIFEST.in

# Install dependencies using UV
RUN uv pip install --system -r requirements.txt
RUN uv pip install --system -e .

# Create necessary directories for persistent storage
RUN mkdir -p /pyrom-persistent/players \
    /pyrom-persistent/world \
    /pyrom-persistent/system

# Expose the default port (1337)
EXPOSE 1337

# Health check - check if the port is listening
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:1337 || exit 1

# Run the MUD server
CMD ["rom24"]

