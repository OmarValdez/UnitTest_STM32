#!/usr/bin/env python3
"""Genera el paquete de evidencia de auditoria (IEC 62304) y el SBOM.

Produce en build/evidence/:
  - sbom.json                 (CycloneDX 1.5 del firmware + componentes)
  - evidencia.md              (indice del lote)
  - evidencia-<ver>-<sha>.zip (reporte estatico + cobertura + Doxygen +
                               matriz de trazabilidad + sbom + binarios)

Es tolerante: si falta algun artefacto, lo omite y lo anota en el indice.
"""
import os
import re
import sys
import json
import glob
import zipfile
import hashlib
import subprocess
import datetime
import uuid

ROOT = os.getcwd()
OUT = os.path.join(ROOT, "build", "evidence")


def run(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return ""


def git_version():
    env = os.environ.get("GIT_DESCRIBE", "").strip()
    if env:
        return env
    v = run("git describe --tags --always 2>/dev/null")
    return v or "0.1"


def git_sha():
    env = os.environ.get("GIT_COMMIT", "").strip()
    if env:
        return env[:7]
    return run("git rev-parse --short HEAD 2>/dev/null") or "unknown"


def proj_name():
    dp = os.path.join(ROOT, "Doxyfile")
    if os.path.isfile(dp):
        for line in open(dp, encoding="utf-8"):
            if line.strip().startswith("PROJECT_NAME"):
                return line.split("=", 1)[1].strip().strip('"')
    return "ST_UnitTest"


def find_version(path, patterns):
    if not os.path.isfile(path):
        return None
    txt = open(path, encoding="utf-8", errors="ignore").read()
    for pat in patterns:
        m = re.search(pat, txt)
        if m:
            return m.group(1)
    return None


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def collect(dirrel):
    base = os.path.join(ROOT, dirrel)
    out = []
    if not os.path.isdir(base):
        return out
    for dp, _, fns in os.walk(base):
        for fn in fns:
            out.append(os.path.join(dp, fn))
    return out


def build_sbom(version, sha):
    fw_bins = glob.glob(os.path.join(ROOT, "build", "DockerDebug", "*.elf"))
    fw_bins += glob.glob(os.path.join(ROOT, "build", "DockerDebug", "*.bin"))
    fw_hashes = [{"alg": "SHA-256", "content": sha256(b)} for b in fw_bins]
    fw = {
        "type": "firmware",
        "name": proj_name(),
        "version": version,
        "purl": "pkg:generic/%s@%s" % (proj_name(), version),
        "hashes": fw_hashes,
    }
    cmsis_ver = find_version(
        os.path.join(ROOT, "Drivers", "CMSIS", "Include", "cmsis_version.h"),
        [r'CMSIS_VERSION_STRING\s+"([\d.]+)"', r'#define\s+CMSIS_VERSION\s+(\d+)'],
    )
    hal_ver = find_version(
        os.path.join(ROOT, "Drivers", "STM32F1xx_HAL_Driver", "Inc", "stm32f1xx_hal.h"),
        [r'HAL_VERSION_STRING\s+"([\d.]+)"', r'#define\s+HAL_VERSION\s+(\d+)'],
    )
    libs = [
        {"type": "library", "name": "CMSIS", "group": "ARM",
         "version": cmsis_ver or "desconocida",
         "purl": "pkg:generic/arm/cmsis@%s" % (cmsis_ver or "unknown")},
        {"type": "library", "name": "STM32F1xx_HAL_Driver", "group": "STMicroelectronics",
         "version": hal_ver or "desconocida",
         "purl": "pkg:generic/st/stm32f1xx-hal@%s" % (hal_ver or "unknown")},
        {"type": "library", "name": "Unity",
         "version": "provista por Ceedling (no versionada en repo)",
         "purl": "pkg:generic/unity@unknown"},
        {"type": "library", "name": "Ceedling",
         "version": "no versionada en repo",
         "purl": "pkg:generic/ceedling@unknown"},
    ]
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": "urn:uuid:" + str(uuid.uuid4()),
        "version": 1,
        "metadata": {
            "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "component": fw,
            "properties": [{"name": "evidence.commit", "value": sha}],
        },
        "components": libs,
    }


def main():
    os.makedirs(OUT, exist_ok=True)
    version = git_version()
    sha = git_sha()
    sbom = build_sbom(version, sha)
    sbom_path = os.path.join(OUT, "sbom.json")
    with open(sbom_path, "w", encoding="utf-8") as f:
        json.dump(sbom, f, indent=2, ensure_ascii=False)

    files_to_zip = [sbom_path]
    included, missing = [], []
    for d in ["build/static", "build/coverage", "docs/html", "build/traceability"]:
        fs = collect(d)
        if fs:
            files_to_zip.extend(fs)
            included.append(d)
        else:
            missing.append(d)

    fw_bins = glob.glob(os.path.join(ROOT, "build", "DockerDebug", "*.elf"))
    fw_bins += glob.glob(os.path.join(ROOT, "build", "DockerDebug", "*.bin"))
    if fw_bins:
        files_to_zip.extend(fw_bins)
        included.append("build/DockerDebug (binarios)")

    idx = ["# Paquete de Evidencia (IEC 62304)", ""]
    idx.append("- Proyecto: %s" % proj_name())
    idx.append("- Version: %s" % version)
    idx.append("- Commit: %s" % sha)
    idx.append("- Fecha (UTC): %s" % datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ"))
    idx.append("")
    idx.append("## Archivos incluidos")
    for f in files_to_zip:
        idx.append("- %s" % os.path.relpath(f, ROOT))
    if missing:
        idx.append("")
        idx.append("## Artefactos no encontrados (omitidos)")
        for m in missing:
            idx.append("- %s" % m)
    idx.append("")
    idx.append("## SBOM")
    idx.append("CycloneDX 1.5 en sbom.json. Componentes: firmware + CMSIS + "
               "STM32F1xx_HAL_Driver + Unity + Ceedling.")
    index_path = os.path.join(OUT, "evidencia.md")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("\n".join(idx) + "\n")
    files_to_zip.append(index_path)

    zip_name = os.path.join(OUT, "evidencia-%s-%s.zip" % (version, sha))
    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files_to_zip:
            z.write(f, os.path.relpath(f, ROOT))

    print("Paquete de evidencia generado: %s" % zip_name)
    print("SBOM: %s (%d componentes)" % (sbom_path, len(sbom["components"]) + 1))
    if missing:
        print("Advertencia: artefactos faltantes: %s" % ", ".join(missing))


if __name__ == "__main__":
    main()
