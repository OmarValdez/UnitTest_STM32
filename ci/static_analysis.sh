#!/usr/bin/env bash
# Análisis estático MISRA-C con cppcheck.
# Nota: el addon MISRA requiere el texto de reglas MISRA-C_2012.txt (licencia
# MISRA). Sin él, cppcheck ejecuta las comprobaciones base y reporta la ausencia
# del addon. Suministrar el archivo en tools/cppcheck/ para habilitar MISRA.
set -euo pipefail

mkdir -p build/static

cppcheck \
    --enable=warning,style,performance,portability,unusedFunction \
    --std=c11 --language=c \
    -I Core/Inc \
    --addon=misra \
    --suppressions-list=tools/cppcheck/misra_suppressions.txt \
    --xml --xml-version=2 \
    Core/Src 2> build/static/cppcheck.xml || true

# Falla el pipeline si hay errores de cppcheck (no warnings).
if grep -q "<error " build/static/cppcheck.xml; then
    echo "❌ cppcheck reporto errores"
    exit 1
fi
echo "✅ Análisis estático completado"
