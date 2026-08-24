#!/usr/bin/env bash
# Ejecuta pruebas unitarias en HOST (gcc) y genera cobertura real con gcovr.
# Se usa project_ci.yml (host gcc) para que los binarios sean ejecutables en x86.
set -euo pipefail

cd tests
bundle install
bundle exec ceedling test:all --project project_ci.yml
if [ $? -ne 0 ]; then
    echo "❌ Ceedling fallo al ejecutar las pruebas"
    exit 1
fi

mkdir -p build/coverage
gcovr --root . \
      --object-directory build/test/out/test_led_logic \
      --gcov-executable gcov \
      --print-summary \
      --html --html-details -o build/coverage/index.html \
      --xml -o build/coverage/coverage.xml

test -f build/coverage/index.html || { echo "❌ No se generó reporte HTML"; exit 1; }
test -f build/coverage/coverage.xml || { echo "❌ No se generó reporte XML"; exit 1; }
echo "✅ Cobertura generada"
