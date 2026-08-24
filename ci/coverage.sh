#!/usr/bin/env bash
# Ejecuta pruebas unitarias en HOST (gcc) y genera cobertura real con gcovr.
# Se usa project_ci.yml (host gcc) para que los binarios sean ejecutables en x86.
set -euo pipefail

cd tests
# BUNDLE_FROZEN=true: usa Gemfile.lock commiteado y NO lo reescribe (evita
# "Permission denied" al intentar escribir sobre el bind-mount 9p).
# En Bundler 4.x el flag --frozen fue removido; se usa la variable de entorno.
BUNDLE_FROZEN=true bundle install
bundle exec ceedling test:all --project project_ci.yml
if [ $? -ne 0 ]; then
    echo "❌ Ceedling fallo al ejecutar las pruebas"
    exit 1
fi
cd /work

mkdir -p build/coverage
gcovr --root . \
      --object-directory tests/build/test/out/test_led_logic \
      --filter Core/Src \
      --gcov-executable gcov \
      --print-summary \
      --html=build/coverage/index.html --html-details \
      --xml=build/coverage/coverage.xml

test -f build/coverage/index.html || { echo "❌ No se generó reporte HTML"; exit 1; }
test -f build/coverage/coverage.xml || { echo "❌ No se generó reporte XML"; exit 1; }
echo "✅ Cobertura generada"
