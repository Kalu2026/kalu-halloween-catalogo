"""
Crea las páginas individuales p/<CODIGO>.html y p/manifest.json leyendo index.html.

Uso (desde la carpeta donde está index.html):
    python generar_paginas_p.py        (en Windows, si no funciona: py generar_paginas_p.py)

Por cada tarjeta de producto del catálogo crea una página que, al compartirla por WhatsApp,
muestra el nombre, la descripción y la foto de ese producto, y abre el catálogo en él.
Se pueden volver a generar todas cuando quieras: siempre quedan iguales a index.html.
Después sube la carpeta p/ completa a tu repositorio.
"""
import json
import re
from html import unescape
from pathlib import Path
from urllib.parse import quote

BASE = "https://kalu2026.github.io/kalu-halloween-catalogo"
RAIZ = Path(__file__).resolve().parent
SALIDA = RAIZ / "p"


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def pagina(name, code, image, desc):
    c = quote(code)
    d = f"{desc} Consulta disponibilidad y precio por WhatsApp."
    return f'''<!doctype html>
<html lang="es">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta name="robots" content="noindex" />
<title>{esc(name)} | Kalú Accesorios</title>
<meta name="description" content="{esc(d)}" />
<meta property="og:type" content="website" />
<meta property="og:locale" content="es_CO" />
<meta property="og:site_name" content="Kalú Accesorios" />
<meta property="og:title" content="{esc(name)} ({esc(code)})" />
<meta property="og:description" content="{esc(d)}" />
<meta property="og:image" content="{BASE}/{image}" />
<meta property="og:url" content="{BASE}/p/{c}.html" />
<meta name="twitter:card" content="summary_large_image" />
<meta http-equiv="refresh" content="0; url=../#producto={c}" />
<script>location.replace("../#producto={c}");</script>
</head>
<body style="font-family:Arial,sans-serif;background:#11031b;color:#fff;text-align:center;padding:32px">
<p>Abriendo {esc(name)}…</p>
<p><a style="color:#ffbd18" href="../#producto={c}">Ver en el catálogo</a></p>
</body>
</html>
'''


def leer_productos(html):
    productos = []
    for tag in re.findall(r'<article class="card[^"]*"[^>]*data-code="[^"]+"[^>]*>', html):
        attrs = {k: unescape(v) for k, v in re.findall(r'data-(name|code|image|desc)="([^"]*)"', tag)}
        if {"name", "code", "image", "desc"} <= attrs.keys():
            productos.append(attrs)
    return productos


if __name__ == "__main__":
    productos = leer_productos((RAIZ / "index.html").read_text(encoding="utf-8"))
    SALIDA.mkdir(exist_ok=True)
    codigos = []
    for p in productos:
        (SALIDA / f"{p['code']}.html").write_text(pagina(p["name"], p["code"], p["image"], p["desc"]), encoding="utf-8", newline="\n")
        codigos.append(p["code"])
    (SALIDA / "manifest.json").write_text(json.dumps(codigos, ensure_ascii=False), encoding="utf-8", newline="\n")
    print(f"Listo: {len(codigos)} páginas creadas en {SALIDA}")
    print("Sube la carpeta p/ completa a tu repositorio.")
