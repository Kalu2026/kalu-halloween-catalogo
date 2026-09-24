"""
Genera las miniaturas del buscador en assets/thumbs/ para TODOS los productos de index.html.

Uso (desde la carpeta del sitio, donde están index.html y assets/):
    pip install pillow
    python generar_miniaturas.py

Cada miniatura: 160x160, fondo blanco, producto recortado y centrado (igual que hacía el
buscador "al vuelo", pero ya lista). Si ya existe, se salta; usa --forzar para rehacerlas.
"""
import re
import sys
from pathlib import Path
from PIL import Image, ImageChops

RAIZ = Path(__file__).resolve().parent
SALIDA = RAIZ / "assets" / "thumbs"
TAM, MARGEN, UMBRAL = 160, 10, 215
forzar = "--forzar" in sys.argv

html = (RAIZ / "index.html").read_text(encoding="utf-8")
rutas = sorted(set(re.findall(r'data-image="([^"]+)"', html)))
SALIDA.mkdir(parents=True, exist_ok=True)


def abrir_en_blanco(ruta):
    img = Image.open(ruta)
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        fondo = Image.new("RGB", img.size, "white")
        fondo.paste(img, mask=img.split()[-1])
        return fondo
    return img.convert("RGB")


def caja_producto(img):
    r, g, b = img.split()
    minimo = ImageChops.darker(ImageChops.darker(r, g), b)
    return minimo.point(lambda v: 255 if v < UMBRAL else 0).getbbox()


hechas = saltadas = faltan = 0
for rel in rutas:
    origen = RAIZ / rel
    destino = SALIDA / (origen.stem + ".jpg")
    if not origen.exists():
        print("  FALTA la imagen:", rel)
        faltan += 1
        continue
    if destino.exists() and not forzar:
        saltadas += 1
        continue
    img = abrir_en_blanco(origen)
    caja = caja_producto(img)
    if caja:
        img = img.crop(caja)
    escala = min((TAM - 2 * MARGEN) / img.width, (TAM - 2 * MARGEN) / img.height)
    nuevo = img.resize((max(1, round(img.width * escala)), max(1, round(img.height * escala))), Image.LANCZOS)
    lienzo = Image.new("RGB", (TAM, TAM), "white")
    lienzo.paste(nuevo, ((TAM - nuevo.width) // 2, (TAM - nuevo.height) // 2))
    lienzo.save(destino, "JPEG", quality=85, optimize=True)
    hechas += 1

print(f"Listo: {hechas} creadas, {saltadas} ya existían, {faltan} imágenes no encontradas.")
print("Sube la carpeta assets/thumbs/ completa a tu repositorio.")
