#!/usr/bin/env bash
# Firma los binarios del firmware con la clave privada montada en /key.pem.
# Se ejecuta DENTRO del contenedor sw-medico (tiene openssl + arm-none-eabi-objcopy).
set -euo pipefail

VERSION="${1:-unknown}"
ELF=build/DockerDebug/ST_UnitTest.elf
BIN=build/DockerDebug/ST_UnitTest.bin
HEX=build/DockerDebug/ST_UnitTest.hex
KEY=/key.pem

if [ ! -f "$KEY" ]; then
    echo "ERROR: clave de firma no montada en $KEY" >&2
    exit 1
fi

arm-none-eabi-objcopy -O ihex "$ELF" "$HEX"

sha256file() { openssl dgst -sha256 -r "$1" | awk '{print $1}'; }
sign() { openssl dgst -sha256 -sign "$KEY" -out "$1.sig" "$1"; }

sign "$ELF"
sign "$BIN"
sign "$HEX"

mkdir -p build
cat > build/signatures.json <<JSON
{
  "version": "$VERSION",
  "algorithm": "RSA-2048 / SHA-256",
  "publicKey": "config/release_pubkey.pem",
  "artifacts": [
    {"file": "ST_UnitTest.elf", "sha256": "$(sha256file "$ELF")", "signature": "ST_UnitTest.elf.sig"},
    {"file": "ST_UnitTest.bin", "sha256": "$(sha256file "$BIN")", "signature": "ST_UnitTest.bin.sig"},
    {"file": "ST_UnitTest.hex", "sha256": "$(sha256file "$HEX")", "signature": "ST_UnitTest.hex.sig"}
  ]
}
JSON

echo "Firmware firmado para $VERSION"
