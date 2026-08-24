#!/usr/bin/env bash
# Analisis estatico: cppcheck (+ MISRA-C si hay reglas) + lizard + flawfinder.
# Los archivos generados por CubeMX se excluyen para no evaluar codigo de vendor.
set -uo pipefail

mkdir -p build/static

SRC=Core/Src
INC=Core/Inc
MISRA_JSON=/opt/misra-config/misra.json
MISRA_TXT=/opt/misra-config/misra.txt
SUPP=tools/cppcheck/misra_suppressions.txt

EXCLUDES=(
  "$SRC/sysmem.c"
  "$SRC/syscalls.c"
  "$SRC/stm32f1xx_hal_msp.c"
  "$SRC/system_stm32f1xx.c"
)
EXTRA=""
for f in "${EXCLUDES[@]}"; do EXTRA="$EXTRA --exclude=$f"; done

# Detectar si MISRA-C esta disponible (requiere el texto de reglas licenciado)
if [ -f "$MISRA_JSON" ] && [ -f "$MISRA_TXT" ]; then
    echo "✅ MISRA-C habilitado (texto de reglas encontrado)"
    ADDON="--addon=$MISRA_JSON"
else
    echo "⚠️ MISRA-C no disponible (falta config/misra.txt). Analisis base solo."
    ADDON=""
fi

cppcheck \
    --enable=warning,style,performance,portability,unusedFunction \
    --std=c11 --language=c \
    -I "$INC" \
    $ADDON \
    --suppressions-list="$SUPP" \
    --xml --xml-version=2 \
    $EXTRA \
    "$SRC" 2> build/static/cppcheck.xml || true

# Falla el pipeline solo si cppcheck reporta errores (no warnings)
if grep -q "<error " build/static/cppcheck.xml; then
    echo "❌ cppcheck reporto errores"
    exit 1
fi

# Complejidad ciclomatica (util para MISRA Rule 17.1 / IEC 62304)
echo "📊 Complejidad ciclomatica (lizard)..."
lizard "$SRC" -C 10 -L 50 -m \
    -x"$SRC/sysmem.c" -x"$SRC/syscalls.c" \
    -x"$SRC/stm32f1xx_hal_msp.c" -x"$SRC/system_stm32f1xx.c" \
    -o build/static/complexity.txt 2>&1 || true

# Analisis de seguridad de codigo (flawfinder)
echo "🔐 flawfinder..."
flawfinder --quiet --minlevel=3 --context --html "$SRC" > build/static/flawfinder.html 2>&1 || true

echo "✅ Analisis estatico completado"
