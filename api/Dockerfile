#builder stage
FROM ubuntu:22.04 AS builder

# non-interactive installs
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    build-essential cmake git libhiredis-dev wget libasio-dev \
    && rm -rf /var/lib/apt/lists/*

# we compile from source since it normally does not work directly when installing the system packages
WORKDIR /tmp
RUN git clone --depth 1 https://github.com/sewenew/redis-plus-plus.git \
    && cd redis-plus-plus \
    && mkdir build && cd build \
    && cmake -DCMAKE_BUILD_TYPE=Release .. \
    && make -j$(nproc) && make install

WORKDIR /app

# currently using crow v.1.3.2 (change if needed)
RUN wget https://github.com/CrowCpp/Crow/releases/download/v1.3.2/crow_all.h

COPY main.cpp .

RUN g++ -O3 main.cpp -lpthread -lredis++ -lhiredis -o ingest_api


# prod stage
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# We only install the runtime dependencies here, NOT the compilers
RUN apt-get update && apt-get install -y libhiredis-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# get the compiled binary
COPY --from=builder /app/ingest_api .

# get compiled redis
COPY --from=builder /usr/local/lib/libredis++.so* /usr/local/lib/

# rerun config for linux to see the libraries
RUN ldconfig

# change when necessary (currently running at port 8080)
EXPOSE 8080

CMD ["./ingest_api"]
