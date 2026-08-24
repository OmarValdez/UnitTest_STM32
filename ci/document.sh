#!/usr/bin/env bash
# Genera la documentación Doxygen (incluye los @req de trazabilidad).
set -euo pipefail

doxygen Doxyfile
echo "✅ Documentación generada en docs/html"
