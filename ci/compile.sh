#!/usr/bin/env bash
# Compila el firmware para el target ARM (cross-compile).
set -euo pipefail

cmake --preset DockerDebug
cmake --build build/DockerDebug --config Debug
arm-none-eabi-objcopy -O binary build/DockerDebug/ST_UnitTest.elf build/DockerDebug/ST_UnitTest.bin
arm-none-eabi-size build/DockerDebug/ST_UnitTest.elf
