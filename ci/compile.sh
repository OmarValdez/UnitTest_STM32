#!/usr/bin/env bash
# Compila el firmware para el target ARM (cross-compile).
# No usa CMakePresets (archivo generado por STM32CubeMX) para no depender de él.
set -euo pipefail

cmake -S . -B build/DockerDebug -G Ninja \
    -DCMAKE_TOOLCHAIN_FILE=cmake/gcc-arm-none-eabi.cmake \
    -DCMAKE_BUILD_TYPE=Debug

cmake --build build/DockerDebug --config Debug

arm-none-eabi-objcopy -O binary build/DockerDebug/ST_UnitTest.elf build/DockerDebug/ST_UnitTest.bin
arm-none-eabi-size build/DockerDebug/ST_UnitTest.elf
