#!/usr/bin/env python3
"""Quality gate de cobertura.

Lee build/coverage/coverage.xml (Cobertura, generado por gcovr) y compara la
cobertura de lineas con el umbral COVERAGE_THRESHOLD (%). Si esta por debajo,
termina con codigo 1 para que Jenkins falle el build (gate de calidad).

Sin coverage.xml (p.ej. cobertura desactivada) no bloquea: sale 0.
"""
import os
import sys
import xml.etree.ElementTree as ET

XML_PATH = "build/coverage/coverage.xml"


def main():
    threshold = float(os.environ.get("COVERAGE_THRESHOLD", "80"))
    if not os.path.exists(XML_PATH):
        print("coverage_gate: %s no encontrado; no se bloquea el build." % XML_PATH)
        sys.exit(0)

    try:
        root = ET.parse(XML_PATH).getroot()
        line_rate = float(root.get("line-rate", "0"))
    except (ET.ParseError, ValueError) as ex:
        print("coverage_gate: no se pudo leer line-rate: %s" % ex)
        sys.exit(0)

    pct = line_rate * 100.0
    print("Cobertura de lineas: %.1f%% (umbral = %.1f%%)" % (pct, threshold))
    if pct < threshold:
        print("❌ Cobertura por debajo del umbral (%.1f%% < %.1f%%)" % (pct, threshold))
        sys.exit(1)
    print("✅ Cobertura cumple el umbral")


if __name__ == "__main__":
    main()
