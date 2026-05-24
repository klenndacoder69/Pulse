# Build stage
FROM ubuntu:22.04 AS builder

RUN apt-get update && apt-get install -y \
    g++ \
    libcurl4-openssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pulse_agent.cpp .
RUN g++ pulse_agent.cpp -o pulse_agent -lcurl -std=c++17

# Run stage (smaller image for production)
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    libcurl4 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /app/pulse_agent .

# The CMD assumes it will receive API_URL from docker-compose
CMD ["./pulse_agent"]
