#!/usr/bin/env python3
"""Quality gate de analisis estatico (MISRA-C y complejidad ciclomatica).

Lee build/static/cppcheck.xml y build/static/complexity.txt y falla el build
(exit 1) si se superan los umbrales:
  - violaciones MISRA-C > MISRA_THRESHOLD, o
  - funciones con CCN > COMPLEXITY_THRESHOLD.

Los umbrales son macros configurables desde Jenkins via env:
  MISRA_THRESHOLD (entero, default 0)
  COMPLEXITY_THRESHOLD (entero, default 10)
"""
import os
import sys
import xml.etree.ElementTree as ET
import re

STATIC = "build/static"
CPPCHECK = os.path.join(STATIC, "cppcheck.xml")
COMPLEXITY = os.path.join(STATIC, "complexity.txt")


def main():
    misra_threshold = int(os.environ.get("MISRA_THRESHOLD", "0"))
    cx_threshold = int(os.environ.get("COMPLEXITY_THRESHOLD", "10"))

    # --- MISRA-C ---
    misra = 0
    if os.path.exists(CPPCHECK):
        try:
            root = ET.parse(CPPCHECK).getroot()
            for e in root.iter("error"):
                i = (e.get("id") or "").lower()
                if i.startswith("misra") and "misra-config" not in i:
                    misra += 1
        except ET.ParseError:
            pass

    # --- Complejidad (lizard, formato texto) ---
    cx = 0
    cx_funcs = []
    if os.path.exists(COMPLEXITY):
        try:
            data = open(COMPLEXITY, encoding="utf-8", errors="ignore").read()
            for line in data.splitlines():
                m = re.match(
                    r"^\s*(?:!>\s*)?\d+\s+(\d+)\s+\d+\s+\d+\s+\d+\s+"
                    r"(\S+?)@(\d+)-(\d+)@(.+?)\s*$", line)
                if m:
                    ccn = int(m.group(1))
                    name = m.group(2)
                    fname = m.group(5)
                else:
                    m2 = re.match(
                        r"^\s*(?:!>\s*)?\d+\s+(\d+)\s+\d+\s+\d+\s+\d+\s+"
                        r"(\S+)\s+(\S+?):(\d+)\s*$", line)
                    if not m2:
                        continue
                    ccn = int(m2.group(1))
                    name = m2.group(2)
                    fname = m2.group(3)
                if ccn > cx_threshold:
                    cx += 1
                    cx_funcs.append((name, fname, ccn))
        except Exception:
            pass

    print("=== Quality Gate (analisis estatico) ===")
    print("MISRA-C: %d violaciones (umbral=%d)" % (misra, misra_threshold))
    print("Complejidad: %d funciones con CCN>%d" % (cx, cx_threshold))

    failed = False
    if misra > misra_threshold:
        print("❌ MISRA-C excede el umbral (%d > %d)" % (misra, misra_threshold))
        failed = True
    if cx > 0:
        print("❌ Funciones demasiado complejas (CCN>%d):" % cx_threshold)
        for n, f, c in cx_funcs:
            print("   - %s (%s) CCN=%d" % (n, f, c))
        failed = True

    if failed:
        sys.exit(1)
    print("✅ Quality gate de analisis estatico superado")


if __name__ == "__main__":
    main()
