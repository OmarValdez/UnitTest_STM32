#!/usr/bin/env python3
"""Genera un reporte HTML unificado de analisis estatico a partir de
cppcheck.xml, complexity.xml (lizard) y flawfinder.html.

Objetivo: presentar los hallazgos de forma navegable y estructurada
(cppcheck, MISRA-C, complejidad, flawfinder) en lugar de dejarlos como
texto plano sujeto a interpretacion. Los archivos crudos quedan
enlazados para auditoria (IEC 62304).
"""
import xml.etree.ElementTree as ET
import os

STATIC = "build/static"
OUT = os.path.join(STATIC, "index.html")
CPPCHECK = os.path.join(STATIC, "cppcheck.xml")
COMPLEXITY = os.path.join(STATIC, "complexity.xml")
FLAWFINDER = os.path.join(STATIC, "flawfinder.html")

cpp_errors = []
misra_count = 0
if os.path.exists(CPPCHECK):
    try:
        root = ET.parse(CPPCHECK).getroot()
        for e in root.iter("error"):
            loc = e.find("location")
            f = e.get("file0") or e.get("file") or \
                (loc.get("file") if loc is not None else "")
            l = e.get("line") or \
                (loc.get("line") if loc is not None else "")
            i = e.get("id", "")
            sev = e.get("severity", "")
            msg = e.get("msg", "")
            cpp_errors.append((f, l, i, sev, msg))
            if i and i.lower().startswith("misra"):
                misra_count += 1
    except ET.ParseError as ex:
        cpp_errors.append(("(xml invalido: %s)" % ex, "", "", "error", ""))

complex_funcs = []
if os.path.exists(COMPLEXITY):
    try:
        root = ET.parse(COMPLEXITY).getroot()
        for file_el in root.iter("file"):
            fname = file_el.get("name", "")
            for m in file_el.iter("method"):
                name = m.get("name", "?")
                line = m.get("line", "")
                ccn = None
                for met in m.iter("metric"):
                    if met.get("name") == "CCN":
                        ccn = met.get("value")
                try:
                    ccn_val = int(ccn) if ccn is not None else 0
                except (ValueError, TypeError):
                    ccn_val = 0
                if ccn_val >= 10:
                    complex_funcs.append((name, fname, line, ccn_val))
    except ET.ParseError as ex:
        complex_funcs.append(("parse error: %s" % ex, "", "", 0))

ff_hits = 0
if os.path.exists(FLAWFINDER):
    try:
        data = open(FLAWFINDER, encoding="utf-8", errors="ignore").read()
        ff_hits = data.count("[Hits]")
    except Exception:
        ff_hits = 0


def esc(s):
    return (str(s) if s is not None else "").replace("&", "&amp;") \
        .replace("<", "&lt;").replace(">", "&gt;")


rows_cpp = "".join(
    "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
        esc(f), esc(l), esc(i), esc(sev), esc(msg))
    for (f, l, i, sev, msg) in cpp_errors) or \
    "<tr><td colspan='5'>Sin hallazgos de cppcheck/MISRA</td></tr>"

rows_cx = "".join(
    "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
        esc(n), esc(f), esc(l), esc(c))
    for (n, f, l, c) in complex_funcs) or \
    "<tr><td colspan='4'>Sin funciones con CCN &gt;= 10</td></tr>"

html_doc = """<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<title>Reporte de Analisis Estatico</title>
<style>
 body{{font-family:sans-serif;margin:2em;color:#223;}}
 h1,h2{{color:#234;}}
 table{{border-collapse:collapse;width:100%;margin-bottom:1em;}}
 th,td{{border:1px solid #ccc;padding:4px 8px;text-align:left;vertical-align:top;}}
 th{{background:#eef;}}
 .summary{{background:#f4f7fb;border:1px solid #cdd;padding:1em;border-radius:6px;}}
 .meta{{color:#667;font-size:.9em;}}
 a{{color:#06c;}}
 .ok{{color:#285;}}
</style></head><body>
<h1>Reporte de Analisis Estatico</h1>
<div class="summary">
 <p><b>Resumen</b></p>
 <ul>
  <li>cppcheck / estilo: <b>{n_cpp}</b> hallazgos</li>
  <li>MISRA-C: <b>{n_misra}</b> violaciones (reporte, no bloquea)</li>
  <li>Complejidad (lizard, CCN &gt;= 10): <b>{n_cx}</b> funciones</li>
  <li>flawfinder: <b>~{n_ff}</b> hallazgos (ver archivo enlazado)</li>
 </ul>
 <p class="meta">Reporte consolidado de cppcheck, MISRA-C, lizard y flawfinder.
 Los archivos crudos estan enlazados abajo para trazabilidad (IEC 62304).</p>
</div>

<h2>cppcheck / MISRA-C</h2>
<table><thead><tr><th>Archivo</th><th>Linea</th><th>ID</th><th>Severidad</th><th>Mensaje</th></tr></thead>
<tbody>{rows_cpp}</tbody></table>

<h2>Complejidad ciclomatica (lizard, CCN &gt;= 10)</h2>
<table><thead><tr><th>Funcion</th><th>Archivo</th><th>Linea</th><th>CCN</th></tr></thead>
<tbody>{rows_cx}</tbody></table>

<h2>Archivos crudos</h2>
<ul>
 <li><a href="cppcheck.xml">cppcheck.xml</a></li>
 <li><a href="complexity.xml">complexity.xml (lizard)</a></li>
 <li><a href="flawfinder.html">flawfinder.html</a> (resultado de flawfinder)</li>
</ul>
</body></html>
""".format(n_cpp=len(cpp_errors), n_misra=misra_count,
           n_cx=len(complex_funcs), n_ff=ff_hits,
           rows_cpp=rows_cpp, rows_cx=rows_cx)

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(html_doc)

print("Reporte estatico generado: %s (%d cppcheck, %d misra, %d complejas, %d flawfinder)"
      % (OUT, len(cpp_errors), misra_count, len(complex_funcs), ff_hits))
