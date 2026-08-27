#!/usr/bin/env bash
# Compila el firmware para el target ARM (cross-compile).
# No usa CMakePresets (archivo generado por STM32CubeMX) para no depender de él.
set -euo pipefail

CMAKE_FLAGS="-S . -B build/DockerDebug -G Ninja \
    -DCMAKE_TOOLCHAIN_FILE=cmake/gcc-arm-none-eabi.cmake \
    -DCMAKE_BUILD_TYPE=Debug"

if [ -n "${FW_VERSION:-}" ]; then
    mkdir -p build
    printf '#define FW_VERSION "%s"\n' "$FW_VERSION" > build/version.h
    CMAKE_FLAGS="$CMAKE_FLAGS -DCMAKE_C_FLAGS=-include/work/build/version.h"
fi

cmake $CMAKE_FLAGS

cmake --build build/DockerDebug --config Debug

arm-none-eabi-objcopy -O binary build/DockerDebug/ST_UnitTest.elf build/DockerDebug/ST_UnitTest.bin
arm-none-eabi-size build/DockerDebug/ST_UnitTest.elf
