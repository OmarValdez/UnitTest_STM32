# Entorno reproducible para el pipeline de firmware (IEC 62304 piloto)
# Base ruby:3.2-slim-bookworm (Debian 12) => Ruby 3.2 (requerido por Ceedling/erb)
# Se fija la distro (bookworm) para no depender del tag flotante ni de trixie.
FROM ruby:3.2-slim-bookworm

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

# --- gcovr (cobertura) y herramientas de analisis estatico auxiliares ---
RUN pip3 install --no-cache-dir gcovr lizard flawfinder cpplint jinja2

# --- cppcheck 2.21.0 desde fuente (compatible con el addon MISRA) ---
RUN apt-get update && apt-get install -y --no-install-recommends \
        pkg-config \
    && rm -rf /var/lib/apt/lists/* \
    && cd /tmp \
    && wget -q https://github.com/cppcheck-opensource/cppcheck/archive/refs/tags/2.21.0.tar.gz \
    && tar -xzf 2.21.0.tar.gz \
    && cd cppcheck-2.21.0 \
    && mkdir build && cd build \
    && cmake .. \
    && make -j"$(nproc)" \
    && make install \
    && cd / && rm -rf /tmp/cppcheck-2.21.0 /tmp/2.21.0.tar.gz

# --- Addon MISRA para cppcheck (misma version 2.21.0 que la compilacion) ---
RUN wget -q https://github.com/cppcheck-opensource/cppcheck/raw/2.21.0/addons/misra.py \
        -O /usr/share/cppcheck/addons/misra.py \
    && chmod +x /usr/share/cppcheck/addons/misra.py

# --- Ceedling / Unity (se hornean las gemas en la imagen) ---
WORKDIR /gemsbuild
COPY Gemfile ./
RUN gem install bundler \
    && bundle install \
    && rm -rf /gemsbuild

# --- Configuracion MISRA del proyecto (misra.json + misra.txt opcional) ---
COPY config/ /opt/misra-config/

WORKDIR /work
ENTRYPOINT ["/bin/bash", "-c"]
