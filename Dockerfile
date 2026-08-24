# Entorno reproducible para el pipeline de firmware (IEC 62304 piloto)
# Base ruby:3.2-slim (Debian bookworm) => Ruby 3.2 (requerido por Ceedling/erb)
FROM ruby:3.2-slim

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    BUNDLE_PATH=/usr/local/bundle

# --- Herramientas base del sistema ---
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        ninja-build \
        python3 \
        python3-pip \
        wget \
        gnupg \
        ca-certificates \
        doxygen \
        graphviz \
        cppcheck \
        gcc-arm-none-eabi \
        gdb-multiarch \
        libicu72 \
        libssl3 \
        libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# --- Renode (simulación de sistema) vía repo oficial ---
RUN wget -qO- https://download.renode.io/apt/keys/renode.key \
        | gpg --dearmor -o /usr/share/keyrings/renode-archive-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/renode-archive-keyring.gpg] https://download.renode.io/apt stable main" \
        > /etc/apt/sources.list.d/renode.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends renode \
    && rm -rf /var/lib/apt/lists/*

# --- gcovr (cobertura) ---
RUN pip3 install --no-cache-dir gcovr

# --- Ceedling / Unity (se hornean las gemas en la imagen) ---
WORKDIR /gemsbuild
COPY Gemfile ./
RUN gem install bundler \
    && bundle install \
    && rm -rf /gemsbuild

WORKDIR /work
ENTRYPOINT ["/bin/bash", "-c"]
