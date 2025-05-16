ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base-debian:bookworm
FROM ${BUILD_FROM}

ENV PIP_BREAK_SYSTEM_PACKAGES=1

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

WORKDIR /usr/wyoming_rapidfuzz_proxy

# Copy proxy files
COPY wyoming_rapidfuzz_proxy ./wyoming_rapidfuzz_proxy
COPY scripts ./
COPY requirements.txt ./	

RUN \
    apt-get update \
    && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt

ENTRYPOINT ["bash", "start.sh"]
