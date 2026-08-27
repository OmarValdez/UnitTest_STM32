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
COMPLEXITY_THRESHOLD = int(os.environ.get("COMPLEXITY_THRESHOLD", "10"))

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
            if ccn > COMPLEXITY_THRESHOLD:
                complex_funcs.append((func_name, fname, line_no, ccn))
    except Exception as ex:
        complex_funcs.append(("parse error: %s" % ex, "", "", 0))

ff_hits_list = []
if os.path.exists(FLAWFINDER):
    try:
        data = open(FLAWFINDER, encoding="utf-8", errors="ignore").read()
        # Cada hallazgo: <li>archivo:linea: <b> [riesgo] </b> (cat) <i> nombre: desc </i>
        pat = re.compile(
            r"<li>(.*?:\d+):\s*<b>\s*\[(\d+)\]\s*</b>\s*\((.*?)\)\s*<i>\s*(.*?):\s*(.*?)</i>",
            re.S)
        for m in pat.finditer(data):
            loc = m.group(1).strip()
            risk = int(m.group(2))
            cat = m.group(3).strip()
            name = m.group(4).strip()
            desc = re.sub(r"<[^>]+>", "", m.group(5)).strip()
            ff_hits_list.append((loc, risk, cat, name, desc))
    except Exception:
        ff_hits_list = []
ff_hits = len(ff_hits_list)


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
     "<tr><td colspan='4'>Sin funciones con CCN &gt; %d</td></tr>" % COMPLEXITY_THRESHOLD

rows_ff = "".join(
    "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
        esc(loc), esc(risk), esc(cat), esc(name), esc(desc))
    for (loc, risk, cat, name, desc) in ff_hits_list) or \
    "<tr><td colspan='5'>Sin hallazgos de flawfinder (nivel &gt;= 1)</td></tr>"

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
 .note{{background:#fbfbf2;border-left:4px solid #d9c64a;padding:.6em 1em;margin:.6em 0;color:#444;}}
 .meta{{color:#667;font-size:.9em;}}
 a{{color:#06c;}}
 .ok{{color:#285;}}
</style></head><body>
<h1>Reporte de Analisis Estatico</h1>
<p class="note">Este reporte consolida <b>cuatro analisis estaticos</b> del
codigo fuente (se analiza sin ejecutarlo), orientados a calidad, seguridad y
cumplimiento para firmware embebido (IEC 62304). El pipeline aplica
<b>Quality Gates</b>: las violaciones <b>MISRA-C</b> y la complejidad ciclomatica
por encima de su umbral <b>bloquean el build</b>; los hallazgos de cppcheck/estilo
y flawfinder son informativos y el equipo los reduce progresivamente. Los
archivos crudos estan enlazados al final para auditoria.</p>

<div class="summary">
 <p><b>Resumen</b></p>
 <ul>
  <li>cppcheck / estilo: <b>{n_cpp}</b> hallazgos</li>
   <li>MISRA-C: <b>{n_misra}</b> violaciones (bloquea el pipeline si &gt; umbral MISRA_THRESHOLD)</li>
   <li>Complejidad (lizard, CCN &gt; {cx_th}): <b>{n_cx}</b> funciones (bloquea si &gt; COMPLEXITY_THRESHOLD)</li>
  <li>flawfinder (seguridad, nivel &gt;= 1): <b>{n_ff}</b> hallazgos</li>
  <li>Total cppcheck + MISRA: <b>{n_total}</b></li>
 </ul>
</div>

<h2>Qué significa cada analisis</h2>
<ul>
 <li><b>cppcheck / estilo</b>: revisa errores, estilo, portabilidad y rendimiento
  (p. ej. variables no inicializadas, conversiones peligrosas, fugas). Un
  <i>warning</i> suele ser un bug potencial; <i>style</i> apunta a practicas que
  dificultan el mantenimiento. No todos son errores, pero conviene revisarlos.</li>
 <li><b>MISRA-C:2012</b>: conjunto de reglas de codificacion segura para C en
  sistemas embebidos (automocion, medical). Cada violacion es una desviacion de
  la guia; para IEC 62304 se documentan y justifican en el QMS. Las supresiones
  autorizadas estan en <code>tools/cppcheck/misra_suppressions.txt</code>.</li>
 <li><b>Complejidad ciclomatica (lizard)</b>: el CCN cuenta los caminos
  independientes de una funcion. A mayor CCN, mas casos de prueba necesarios y
   mayor probabilidad de defectos. Por convencion, <b>CCN &gt; {cx_th}</b> indica una
   funcion dificil de probar/mantener y candidata a refactorizar.</li>
 <li><b>flawfinder</b>: escaneo de seguridad que busca funciones C/C++ peligrosas
  (p. ej. <code>strcpy</code>, <code>gets</code>) y patrones de desbordamiento de
  buffer. El "Riesgo" va de 1 (bajo) a 5 (alto); aqui se reporta nivel &gt;= 1.</li>
</ul>

<h2>cppcheck / estilo</h2>
<table><thead><tr><th>Archivo</th><th>Linea</th><th>ID</th><th>Severidad</th><th>Mensaje</th></tr></thead>
<tbody>{rows_cpp_style}</tbody></table>

<h2>MISRA-C</h2>
<table><thead><tr><th>Archivo</th><th>Linea</th><th>ID</th><th>Severidad</th><th>Mensaje</th></tr></thead>
<tbody>{rows_misra}</tbody></table>

<h2>Complejidad ciclomatica (lizard, CCN &gt; 10)</h2>
<p class="note">Funciones cuya complejidad supera el umbral. Se recomienda
dividirlas en funciones mas pequenas y con un solo proposito para facilitar
pruebas y reducir el riesgo de defectos.</p>
<table><thead><tr><th>Funcion</th><th>Archivo</th><th>Linea</th><th>CCN</th></tr></thead>
<tbody>{rows_cx}</tbody></table>

<h2>Analisis de seguridad (flawfinder)</h2>
<p class="note">Cada hallazgo es una funcion potencialmente insegura. El nivel de
riesgo (1-5) orienta la prioridad: revision inmediata para los de mayor riesgo.
No todo hallazgo es una vulnerabilidad real, pero debe revisarse y, si aplica,
sustituirse por una alternativa segura (p. ej. <code>snprintf</code> en lugar de
<code>strcpy</code>).</p>
<table><thead><tr><th>Ubicacion</th><th>Riesgo</th><th>Categoria</th><th>Funcion</th><th>Descripcion</th></tr></thead>
<tbody>{rows_ff}</tbody></table>

<h2>Trazabilidad de requisitos (IEC 62304)</h2>
<p class="note">La trazabilidad requisito &rarr; c&oacute;digo &rarr; pruebas se genera con
Doxygen a partir de la etiqueta <code>@requirement</code> (p. ej. ICN-SW-001/002/003).
La p&aacute;gina <b>Requisitos</b> de la documentaci&oacute;n Doxygen agrupa cada
requisito con su implementaci&oacute;n (<code>Core/User/Src/led_logic.c</code>) y sus
pruebas unitarias (<code>tests/test/test_led_logic.c</code>). Los Requerimientos de
software est&aacute;n en <code>requirements/requerimientos.md</code>.</p>

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
           cx_th=COMPLEXITY_THRESHOLD,
           n_total=len(cpp_style) + len(misra_errors),
           rows_cpp_style=rows_cpp_style, rows_misra=rows_misra,
           rows_cx=rows_cx, rows_ff=rows_ff)

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(html_doc)

print("Reporte estatico generado: %s (%d cppcheck/estilo, %d misra, %d complejas, %d flawfinder)"
      % (OUT, len(cpp_style), len(misra_errors), len(complex_funcs), ff_hits))
