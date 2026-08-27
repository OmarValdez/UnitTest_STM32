#!/usr/bin/env python3
"""Genera la matriz de trazabilidad de requisitos (IEC 62304).

Escanea las etiquetas `@requirement <ID> <texto>` en el c\u00f3digo, las pruebas
y el spec de requerimientos, y produce:
  - build/traceability/matrix.html  (tabla publicable en el dashboard de Jenkins)
  - build/traceability/matrix.pdf   (evidencia en PDF, sin dependencias externas)
  - build/traceability/matrix.md    (copia en Markdown)

Como el script escanea din\u00e1micamente, basta con agregar `@requirement ID texto`
en requirements/requerimientos.md (y referenciarlo en c\u00f3digo/pruebas) para que
la matriz se regenere sola en el siguiente build.
"""
import os
import re

ROOT = os.getcwd()
OUT_DIR = os.path.join(ROOT, "build", "traceability")
REQ_RE = re.compile(r"@requirement\s+([A-Za-z0-9_\-]+)\s+(.*?)\s*$")
SCAN_DIRS = [
    os.path.join(ROOT, "requirements"),
    os.path.join(ROOT, "Core"),
    os.path.join(ROOT, "tests"),
]


def classify(fpath):
    p = os.path.normpath(fpath)
    parts = p.split(os.sep)
    if "tests" in parts:
        return "test"
    if "requirements" in parts:
        return "spec"
    return "impl"


def scan():
    reqs = {}          # id -> texto del requisito
    refs = {}          # id -> {'impl': set, 'test': set}
    for base in SCAN_DIRS:
        if not os.path.isdir(base):
            continue
        for dirpath, _, files in os.walk(base):
            if "build" in dirpath.split(os.sep) or "docs" in dirpath.split(os.sep):
                continue
            for fn in files:
                if not fn.endswith((".c", ".h", ".md")):
                    continue
                fpath = os.path.join(dirpath, fn)
                try:
                    with open(fpath, "r", encoding="utf-8") as fh:
                        lines = fh.readlines()
                except Exception:
                    continue
                rel = os.path.relpath(fpath, ROOT)
                for i, line in enumerate(lines, 1):
                    m = REQ_RE.search(line)
                    if not m:
                        continue
                    rid, text = m.group(1), m.group(2).strip()
                    if rid not in reqs:
                        reqs[rid] = text
                    # El spec es la definicion; no cuenta como impl/test.
                    if classify(fpath) == "test":
                        refs.setdefault(rid, {"impl": set(), "test": set()})["test"].add("%s:%d" % (rel, i))
                    elif classify(fpath) == "impl":
                        refs.setdefault(rid, {"impl": set(), "test": set()})["impl"].add("%s:%d" % (rel, i))
    return reqs, refs


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def write_html(reqs, refs):
    rows = []
    for rid in sorted(reqs):
        r = refs.get(rid, {"impl": set(), "test": set()})
        impl = "<br>".join(esc(x) for x in sorted(r["impl"])) or "<i>-- sin implementaci\u00f3n --</i>"
        test = "<br>".join(esc(x) for x in sorted(r["test"])) or "<i>-- sin pruebas --</i>"
        rows.append(
            "<tr><td><b>%s</b></td><td>%s</td><td>%s</td><td>%s</td></tr>"
            % (esc(rid), esc(reqs[rid]), impl, test)
        )
    html = """<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<title>Matriz de Trazabilidad de Requisitos</title>
<style>
 body{font-family:sans-serif;margin:2em;color:#223;}
 h1{color:#234;}
 table{border-collapse:collapse;width:100%%;}
 th,td{border:1px solid #ccc;padding:6px 8px;text-align:left;vertical-align:top;}
 th{background:#eef;}
 .meta{color:#667;font-size:.9em;}
 .gap{color:#b22;}
</style></head><body>
<h1>Matriz de Trazabilidad de Requisitos (IEC 62304)</h1>
<p class="meta">Requisito &rarr; Implementaci\u00f3n &rarr; Pruebas. Generada
autom\u00e1ticamente desde las etiquetas <code>@requirement</code>. Las celdas
<i>-- sin implementaci\u00f3n --</i> / <i>-- sin pruebas --</i> indican brechas
de trazabilidad.</p>
<table><thead><tr><th>ID</th><th>Requisito</th><th>Implementaci\u00f3n</th><th>Pruebas</th></tr></thead>
<tbody>%s</tbody></table>
</body></html>""" % "\n".join(rows)
    with open(os.path.join(OUT_DIR, "matrix.html"), "w", encoding="utf-8") as fh:
        fh.write(html)


def write_md(reqs, refs):
    lines = ["# Matriz de Trazabilidad de Requisitos", "",
             "| ID | Requisito | Implementación | Pruebas |",
             "|----|----------|----------------|---------|"]
    for rid in sorted(reqs):
        r = refs.get(rid, {"impl": set(), "test": set()})
        impl = ", ".join(sorted(r["impl"])) or "-- sin implementación --"
        test = ", ".join(sorted(r["test"])) or "-- sin pruebas --"
        lines.append("| %s | %s | %s | %s |" % (rid, reqs[rid], impl, test))
    with open(os.path.join(OUT_DIR, "matrix.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def write_pdf(reqs, refs):
    """PDF m\u00ednimo y autocontenido (Courier, sin librer\u00edas externas)."""
    W, H = 612, 792
    left, top, bottom = 40, 750, 40
    leading = 13
    lines = ["MATRIZ DE TRAZABILIDAD DE REQUISITOS (IEC 62304)", ""]
    for rid in sorted(reqs):
        r = refs.get(rid, {"impl": set(), "test": set()})
        lines.append("ID: %s" % rid)
        lines.append("Req: %s" % reqs[rid])
        lines.append("Impl: " + (", ".join(sorted(r["impl"])) or "-- sin implementacion --"))
        lines.append("Test: " + (", ".join(sorted(r["test"])) or "-- sin pruebas --"))
        lines.append("")
    # paginar
    pages, cur, y = [], [], top
    for ln in lines:
        cur.append(ln)
        y -= leading
        if y < bottom:
            pages.append(cur)
            cur, y = [], top
    if cur:
        pages.append(cur)
    n = len(pages)
    page_nums = [4 + 2 * i for i in range(n)]
    content_nums = [5 + 2 * i for i in range(n)]
    objs = {}
    objs[1] = "<< /Type /Catalog /Pages 2 0 R >>"
    kids = " ".join("%d 0 R" % p for p in page_nums)
    objs[2] = "<< /Type /Pages /Kids [%s] /Count %d >>" % (kids, n)
    objs[3] = "<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>"
    for i in range(n):
        body = "BT\n/F3 9 Tf\n%d %d Td\n" % (left, top)
        first = True
        for ln in pages[i]:
            s = ln.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            if first:
                body += "(%s) Tj\n" % s
                first = False
            else:
                body += "0 -%d Td (%s) Tj\n" % (leading, s)
        body += "ET"
        objs[content_nums[i]] = "<< /Length %d >>\nstream\n%s\nendstream" % (len(body), body)
        objs[page_nums[i]] = ("<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %d %d] "
                              "/Resources << /Font << /F3 3 0 R >> >> /Contents %d 0 R >>"
                              % (W, H, content_nums[i]))
    out = b"%PDF-1.4\n"
    offsets = {}
    for num in range(1, 3 + 2 * n + 1):
        offsets[num] = len(out)
        out += ("%d 0 obj\n%s\nendobj\n" % (num, objs[num])).encode("latin-1")
    xref = len(out)
    out += ("xref\n0 %d\n" % (3 + 2 * n + 1)).encode("latin-1")
    out += b"0000000000 65535 f \n"
    for num in range(1, 3 + 2 * n + 1):
        out += ("%010d 00000 n \n" % offsets[num]).encode("latin-1")
    out += ("trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n"
            % (3 + 2 * n + 1, xref)).encode("latin-1")
    with open(os.path.join(OUT_DIR, "matrix.pdf"), "wb") as fh:
        fh.write(out)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    reqs, refs = scan()
    write_html(reqs, refs)
    write_md(reqs, refs)
    write_pdf(reqs, refs)
    print("Matriz de trazabilidad generada: %d requisitos en %s"
          % (len(reqs), OUT_DIR))


if __name__ == "__main__":
    main()
