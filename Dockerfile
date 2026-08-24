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
        libnewlib-arm-none-eabi \
        gdb-multiarch \
        libicu72 \
        libssl3 \
        libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# --- Renode (simulación de sistema) vía tarball portable ---
# Se usa el portable en vez del repo apt para evitar problemas de llaves GPG.
# El portable incrusta su propio runtime (Mono), no requiere dependencias apt.
RUN wget -q https://builds.renode.io/renode-latest.linux-portable.tar.gz -O /tmp/renode.tar.gz \
    && mkdir -p /opt/renode \
    && tar xf /tmp/renode.tar.gz -C /opt/renode --strip-components=1 \
    && rm -f /tmp/renode.tar.gz
ENV PATH="/opt/renode:${PATH}"

    # --- gcovr (cobertura) y herramientas de analisis estatico auxiliares ---
    # --break-system-packages: Debian bookworm marca pip como externally-managed (PEP 668).
    # Aceptable en un contenedor desechable de CI.
    RUN pip3 install --no-cache-dir --break-system-packages gcovr lizard flawfinder cpplint jinja2

# --- cppcheck 2.21.0 desde fuente (compatible con el addon MISRA) ---
# Prefijo /usr para que los addons queden en /usr/share/cppcheck/addons
# (donde cppcheck resuelve --addon=misra). Copiamos misra.py del arbol
# fuente para no depender de si 'make install' instala o no los addons.
RUN apt-get update && apt-get install -y --no-install-recommends \
        pkg-config \
    && rm -rf /var/lib/apt/lists/* \
    && cd /tmp \
    && wget -q https://github.com/cppcheck-opensource/cppcheck/archive/refs/tags/2.21.0.tar.gz \
    && tar -xzf 2.21.0.tar.gz \
    && cd cppcheck-2.21.0 \
    && mkdir build && cd build \
    && cmake -DCMAKE_INSTALL_PREFIX=/usr .. \
    && make -j"$(nproc)" \
    && make install \
    && mkdir -p /usr/share/cppcheck/addons \
    && cp /tmp/cppcheck-2.21.0/addons/misra.py /usr/share/cppcheck/addons/misra.py \
    && chmod +x /usr/share/cppcheck/addons/misra.py \
    && cd / && rm -rf /tmp/cppcheck-2.21.0 /tmp/2.21.0.tar.gz

# --- Ceedling / Unity (se hornean las gemas en la imagen) ---
# Se fija la version de Bundler para reproducibilidad (debe coincidir con
# BUNDLED WITH en Gemfile.lock).
WORKDIR /gemsbuild
COPY Gemfile ./
RUN gem install bundler -v 4.0.19 \
    && bundle install \
    && rm -rf /gemsbuild

# --- Configuracion MISRA del proyecto (misra.json + misra.txt opcional) ---
COPY config/ /opt/misra-config/

# Descarga del texto de reglas MISRA-C:2012 (formato cppcheck) desde GitLab.
# Solo si no se proveyo uno localmente en config/misra.txt (tiene prioridad).
# Nota licencia: CC BY-NC-ND 4.0 -> revisar compatibilidad con uso comercial.
RUN if [ ! -f /opt/misra-config/misra.txt ]; then \
        wget -q "https://gitlab.com/MISRA/MISRA-C/MISRA-C-2012/tools/-/raw/main/misra_c_2012__headlines_for_cppcheck%20-%20AMD1%2BAMD2.txt" \
            -O /opt/misra-config/misra.txt \
        && echo "✅ misra.txt descargado de GitLab" \
        || echo "⚠️ No se pudo descargar misra.txt (¿repo privado?). MISRA deshabilitado."; \
    else \
        echo "ℹ️ Usando misra.txt local de config/"; \
    fi

WORKDIR /work
