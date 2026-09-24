#!/usr/bin/env python3
"""Convierte las fotos de assets/ a WebP (máx. 1000 px de ancho) y actualiza index.html.
Uso (desde la carpeta del sitio):   pip install pillow   y luego   python optimizar_imagenes.py
Guarda una copia en index.backup.html y NO borra las imágenes originales."""
import shutil
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).parent
HTML = ROOT / "index.html"
html = HTML.read_text(encoding="utf-8")
shutil.copy(HTML, ROOT / "index.backup.html")
antes = despues = n = 0
for f in sorted((ROOT / "assets").rglob("*")):
    if f.suffix.lower() not in (".jpg", ".jpeg", ".png") or "logo" in f.name.lower():
        continue
    out = f.with_suffix(".webp")
    with Image.open(f) as im:
        im.thumbnail((1000, 1800))
        im = im.convert("RGBA" if "A" in im.getbands() else "RGB")
        im.save(out, "WEBP", quality=80, method=6)
    html = html.replace(f.relative_to(ROOT).as_posix(), out.relative_to(ROOT).as_posix())
    antes += f.stat().st_size; despues += out.stat().st_size; n += 1
HTML.write_text(html, encoding="utf-8")
print(f"{n} imágenes convertidas: {antes/1e6:.1f} MB -> {despues/1e6:.1f} MB")
