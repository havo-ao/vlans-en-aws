#!/usr/bin/env python3
"""Une las partes de la presentación en un solo HTML autocontenido (imágenes incrustadas)."""
import base64, mimetypes, pathlib, re

AQUI = pathlib.Path(__file__).parent
partes = sorted((AQUI / "src").glob("*.html"))
slides = "\n".join(p.read_text(encoding="utf-8") for p in partes)
html = (AQUI / "plantilla.html").read_text(encoding="utf-8").replace("{{slides}}", slides)

def incrustar(m):
    ruta = AQUI / m.group(1)
    tipo = mimetypes.guess_type(ruta.name)[0] or "application/octet-stream"
    return f"data:{tipo};base64,{base64.b64encode(ruta.read_bytes()).decode()}"

html = re.sub(r"\{\{img:([^}]+)\}\}", incrustar, html)
salida = AQUI / "VLANs_en_AWS.html"
salida.write_text(html, encoding="utf-8")
pagina = AQUI.parent / "docs" / "index.html"   # copia que publica GitHub Pages
pagina.parent.mkdir(exist_ok=True)
pagina.write_text(html, encoding="utf-8")
print(f"{salida} · {len(partes)} partes · {salida.stat().st_size // 1024} KB")
