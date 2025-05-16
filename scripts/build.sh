BUILD_FROM=ghcr.io/home-assistant/amd64-base-debian:bookworm
WYOMING_RAPIDFUZZ_PROXY_VERSION=0.0.1
docker build --build-arg BUILD_FROM=${BUILD_FROM} \
      --build-arg WYOMING_RAPIDFUZZ_PROXY=${WYOMING_RAPIDFUZZ_PROXY_VERSION} \
      -t wyoming-rapidfuzz-proxy:${WYOMING_RAPIDFUZZ_PROXY_VERSION} \
      -f Dockerfile .
