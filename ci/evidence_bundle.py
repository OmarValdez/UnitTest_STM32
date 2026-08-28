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


def read_text(path):
    if not os.path.isfile(path):
        return ""
    return open(path, encoding="utf-8", errors="ignore").read()


def parse_int(txt, pat):
    m = re.search(pat, txt)
    if not m:
        return None
    s = m.group(1)
    try:
        return int(s, 16) if s.lower().startswith("0x") else int(s)
    except ValueError:
        return None


def git_version():
    env = os.environ.get("GIT_DESCRIBE", "").strip()
    if env:
        return env
    v = run("git describe --tags --always 2>/dev/null")
    return v or "0.1"


def fw_version_from_header():
    p = os.path.join(ROOT, "build", "version.h")
    if os.path.isfile(p):
        m = re.search(r'#define\s+FW_VERSION\s+"([^"]+)"', read_text(p))
        if m:
            return m.group(1)
    return None


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


def cmsis_core_version():
    t = read_text(os.path.join(ROOT, "Drivers", "CMSIS", "Include", "cmsis_version.h"))
    main = parse_int(t, r'__CM_CMSIS_VERSION_MAIN\s*\(\s*(0x[0-9A-Fa-f]+|\d+)')
    sub = parse_int(t, r'__CM_CMSIS_VERSION_SUB\s*\(\s*(0x[0-9A-Fa-f]+|\d+)')
    if main is None:
        return None
    return "%d.%d" % (main, sub if sub is not None else 0)


def cmsis_device_version():
    t = read_text(os.path.join(ROOT, "Drivers", "CMSIS", "Device", "ST",
                               "STM32F1xx", "Include", "stm32f1xx.h"))
    main = parse_int(t, r'__STM32F1_CMSIS_VERSION_MAIN\s*\(\s*(0x[0-9A-Fa-f]+|\d+)')
    sub1 = parse_int(t, r'__STM32F1_CMSIS_VERSION_SUB1\s*\(\s*(0x[0-9A-Fa-f]+|\d+)')
    sub2 = parse_int(t, r'__STM32F1_CMSIS_VERSION_SUB2\s*\(\s*(0x[0-9A-Fa-f]+|\d+)')
    if main is None:
        return None
    return "%d.%d.%d" % (main, sub1 or 0, sub2 or 0)


def hal_version():
    t = read_text(os.path.join(ROOT, "Drivers", "STM32F1xx_HAL_Driver",
                               "Inc", "stm32f1xx_hal.h"))
    main = parse_int(t, r'__STM32F1xx_HAL_VERSION_MAIN\s*\(\s*(0x[0-9A-Fa-f]+|\d+)')
    sub1 = parse_int(t, r'__STM32F1xx_HAL_VERSION_SUB1\s*\(\s*(0x[0-9A-Fa-f]+|\d+)')
    sub2 = parse_int(t, r'__STM32F1xx_HAL_VERSION_SUB2\s*\(\s*(0x[0-9A-Fa-f]+|\d+)')
    if main is not None:
        return "%d.%d.%d" % (main, sub1 or 0, sub2 or 0)
    m = re.search(r'(?:V|v|Version\s*:?\s*)([0-9]+\.[0-9]+\.[0-9]+)', t)
    if m:
        return m.group(1)
    return None


def gemlock_version(name):
    t = read_text(os.path.join(ROOT, "Gemfile.lock"))
    if not t:
        return None
    m = re.search(r'^[ \t]*' + re.escape(name) + r'\s*\(([^)]+)\)', t, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return None


def compiler_version():
    out = run("arm-none-eabi-gcc --version")
    if out:
        return out.splitlines()[0].strip()
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
    cmsis_core = cmsis_core_version()
    cmsis_dev = cmsis_device_version()
    hal = hal_version()
    ceedling = gemlock_version("ceedling")
    unity = gemlock_version("unity")
    compiler = compiler_version()
    libs = [
        {"type": "library", "name": "CMSIS-Core", "group": "ARM",
         "version": cmsis_core or "desconocida",
         "purl": "pkg:generic/arm/cmsis-core@%s" % (cmsis_core or "unknown")},
        {"type": "library", "name": "CMSIS-Device STM32F1", "group": "ARM",
         "version": cmsis_dev or "desconocida",
         "purl": "pkg:generic/arm/cmsis-device-stm32f1@%s" % (cmsis_dev or "unknown")},
        {"type": "library", "name": "STM32F1xx_HAL_Driver", "group": "STMicroelectronics",
         "version": hal or "no especificada en cabeceras (HAL_GetHalVersion en runtime)",
         "purl": "pkg:generic/st/stm32f1xx-hal@%s" % (hal or "unknown")},
        {"type": "library", "name": "Ceedling", "group": "ThrowTheSwitch",
         "version": ceedling or "no fijada (Gemfile.lock ausente)",
         "purl": "pkg:gem/ceedling@%s" % (ceedling or "unknown")},
        {"type": "library", "name": "Unity", "group": "ThrowTheSwitch",
         "version": unity or "no fijada (Gemfile.lock ausente)",
         "purl": "pkg:gem/unity@%s" % (unity or "unknown")},
        {"type": "library", "name": "GNU Arm Embedded GCC", "group": "ARM",
         "version": compiler or "desconocida",
         "purl": "pkg:generic/gcc-arm-none-eabi@%s" % (compiler or "unknown")},
    ]
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": "urn:uuid:" + str(uuid.uuid4()),
        "version": 1,
        "metadata": {
            "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "component": fw,
            "properties": [
                {"name": "evidence.commit", "value": sha},
                {"name": "evidence.toolchain", "value": compiler or "desconocida"},
            ],
        },
        "components": libs,
    }


def main():
    os.makedirs(OUT, exist_ok=True)
    version = fw_version_from_header() or git_version()
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
    idx.append("## SBOM (CycloneDX 1.5)")
    idx.append("Componentes: firmware + CMSIS-Core + CMSIS-Device STM32F1 + "
               "STM32F1xx_HAL_Driver + Ceedling + Unity + GNU Arm Embedded GCC.")
    for c in sbom["components"]:
        idx.append("- %s@%s" % (c["name"], c["version"]))
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
