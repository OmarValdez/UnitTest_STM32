#!/usr/bin/env bash
# Ejecuta la simulación de sistema en Renode y verifica el marcador de fin.
set -euo pipefail

cd renodescripts
renode --console --disable-xwt -e "include @stm32f103_led_sim.resc" > renode_output.log 2>&1
cat renode_output.log
grep -q "SIMULACION FINALIZADA" renode_output.log || {
    echo "⚠️ No se encontro el marcador de finalizacion de la simulacion"
    exit 1
}
