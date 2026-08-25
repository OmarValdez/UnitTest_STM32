#!/usr/bin/env python3
"""Genera un reporte HTML unificado de analisis estatico a partir de
cppcheck.xml, complexity.txt (reporte texto de lizard) y flawfinder.html.

Objetivo: presentar los hallazgos de forma navegable y estructurada
(cppcheck, MISRA-C, complejidad, flawfinder) en lugar de dejarlos como
texto plano sujeto a interpretacion. Los archivos crudos quedan
enlazados para auditoria (IEC 62304).
"""
import xml.etree.ElementTree as ET
import os
import re

STATIC = "build/static"
OUT = os.path.join(STATIC, "index.html")
CPPCHECK = os.path.join(STATIC, "cppcheck.xml")
COMPLEXITY = os.path.join(STATIC, "complexity.txt")
FLAWFINDER = os.path.join(STATIC, "flawfinder.html")

cpp_style = []
misra_errors = []
if os.path.exists(CPPCHECK):
    try:
        root = ET.parse(CPPCHECK).getroot()
        for e in root.iter("error"):
            loc = e.find("location")
            f = e.get("file0") or e.get("file") or \
                (loc.get("file") if loc is not None else "")
            l = e.get("line0") or e.get("line") or \
                (loc.get("line") if loc is not None else "")
            i = e.get("id", "")
            sev = e.get("severity", "")
            msg = e.get("msg", "")
            rec = (f, l, i, sev, msg)
            if i and i.lower().startswith("misra") and "misra-config" not in i.lower():
                misra_errors.append(rec)
            else:
                cpp_style.append(rec)
    except ET.ParseError as ex:
        cpp_style.append(("(xml invalido: %s)" % ex, "", "", "error", ""))

complex_funcs = []
if os.path.exists(COMPLEXITY):
    try:
        data = open(COMPLEXITY, encoding="utf-8", errors="ignore").read()
        # Formato texto de lizard (estable entre versiones):
        #   NLOC  CCN  token  PARAM  length  location
        #   <n>   <ccn> <tok>  <par>  <len>   nombre@inicio-fin@archivo
        # (versiones antiguas usan "nombre  archivo:linea")
        for line in data.splitlines():
            m = re.match(
                r"^\s*(?:!>\s*)?\d+\s+(\d+)\s+\d+\s+\d+\s+\d+\s+"
                r"(\S+?)@(\d+)-(\d+)@(.+?)\s*$",
                line)
            if m:
                ccn = int(m.group(1))
                func_name = m.group(2)
                line_no = m.group(3)
                fname = m.group(5)
            else:
                m2 = re.match(
                    r"^\s*(?:!>\s*)?\d+\s+(\d+)\s+\d+\s+\d+\s+\d+\s+"
                    r"(\S+)\s+(\S+?):(\d+)\s*$",
                    line)
                if not m2:
                    continue
                ccn = int(m2.group(1))
                func_name = m2.group(2)
                fname = m2.group(3)
                line_no = m2.group(4)
            if ccn > 10:
                complex_funcs.append((func_name, fname, line_no, ccn))
    except Exception as ex:
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


rows_cpp_style = "".join(
    "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
        esc(f), esc(l), esc(i), esc(sev), esc(msg))
    for (f, l, i, sev, msg) in cpp_style) or \
    "<tr><td colspan='5'>Sin hallazgos de cppcheck/estilo</td></tr>"

rows_misra = "".join(
    "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
        esc(f), esc(l), esc(i), esc(sev), esc(msg))
    for (f, l, i, sev, msg) in misra_errors) or \
    "<tr><td colspan='5'>Sin violaciones MISRA-C</td></tr>"

rows_cx = "".join(
    "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
        esc(n), esc(f), esc(l), esc(c))
    for (n, f, l, c) in complex_funcs) or \
    "<tr><td colspan='4'>Sin funciones con CCN &gt; 10</td></tr>"

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
  <li>Complejidad (lizard, CCN &gt; 10): <b>{n_cx}</b> funciones</li>
  <li>flawfinder: <b>~{n_ff}</b> hallazgos (ver archivo enlazado)</li>
  <li>Total cppcheck + MISRA: <b>{n_total}</b></li>
 </ul>
 <p class="meta">Reporte consolidado de cppcheck, MISRA-C, lizard y flawfinder.
 Las violaciones MISRA-C se listan por separado de los hallazgos de cppcheck/estilo.
 Los archivos crudos estan enlazados abajo para trazabilidad (IEC 62304).</p>
</div>

<h2>cppcheck / estilo</h2>
<table><thead><tr><th>Archivo</th><th>Linea</th><th>ID</th><th>Severidad</th><th>Mensaje</th></tr></thead>
<tbody>{rows_cpp_style}</tbody></table>

<h2>MISRA-C</h2>
<table><thead><tr><th>Archivo</th><th>Linea</th><th>ID</th><th>Severidad</th><th>Mensaje</th></tr></thead>
<tbody>{rows_misra}</tbody></table>

<h2>Complejidad ciclomatica (lizard, CCN &gt; 10)</h2>
<table><thead><tr><th>Funcion</th><th>Archivo</th><th>Linea</th><th>CCN</th></tr></thead>
<tbody>{rows_cx}</tbody></table>

<h2>Archivos crudos</h2>
<ul>
 <li><a href="cppcheck.xml">cppcheck.xml</a></li>
 <li><a href="complexity.txt">complexity.txt (reporte lizard)</a></li>
 <li><a href="complexity.xml">complexity.xml (cppncss crudo, Jenkins)</a></li>
 <li><a href="flawfinder.html">flawfinder.html</a> (resultado de flawfinder)</li>
</ul>
</body></html>
""".format(n_cpp=len(cpp_style), n_misra=len(misra_errors),
           n_cx=len(complex_funcs), n_ff=ff_hits,
           n_total=len(cpp_style) + len(misra_errors),
           rows_cpp_style=rows_cpp_style, rows_misra=rows_misra,
           rows_cx=rows_cx)

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(html_doc)

print("Reporte estatico generado: %s (%d cppcheck/estilo, %d misra, %d complejas, %d flawfinder)"
      % (OUT, len(cpp_style), len(misra_errors), len(complex_funcs), ff_hits))
