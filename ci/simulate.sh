#!/usr/bin/env bash
# Ejecuta la simulación de sistema en Renode y verifica el marcador de fin.
set -euo pipefail

cd renodescripts
# El log va a /tmp (fuera del bind-mount 9p) para evitar "Permission denied"
# al sobrescribir el archivo preexistente en el workspace del agente.
renode --console --disable-xwt -e "include @stm32f103_led_sim.resc" > /tmp/renode_output.log 2>&1
cat /tmp/renode_output.log
grep -q "SIMULACION FINALIZADA" /tmp/renode_output.log || {
    echo "⚠️ No se encontro el marcador de finalizacion de la simulacion"
    exit 1
}
