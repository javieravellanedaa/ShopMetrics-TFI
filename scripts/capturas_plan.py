# -*- coding: utf-8 -*-
"""Recorta del plan de trabajo el bloque de cada semana.

El corte no se hace buscando lineas en la imagen: al rasterizar, los bordes de
las tablas salen del mismo gris que el separador de semanas y no hay forma
confiable de distinguirlos. Se usa la posicion real del titulo "Semana N" en el
PDF, que pypdf entrega junto con el texto, y se recorta desde ahi hasta el
titulo siguiente.

    python3 scripts/capturas_plan.py
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile

import pypdf
from PIL import Image, ImageOps

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAN = os.path.join(os.path.dirname(RAIZ), "planificacion_de_proyecto.pdf")
DESTINO = os.path.join(RAIZ, "documento", "img_cierre")

PRIMERA_PAGINA = 5      # donde arranca el detalle semana por semana
ANCHO = 1700            # pixeles de ancho al rasterizar; alcanza para imprimir
AIRE = 26               # margen alrededor del recorte

# La altura que ocupa el renglon del titulo por encima de su linea base. El PDF
# da la posicion de la base, asi que sin esto el recorte parte el titulo al
# medio arriba, y abajo deja asomando el de la semana siguiente.
RENGLON = 52
TITULO = re.compile(r"^Semana (\d+)\s*·")


def rasterizar(pagina: int, carpeta: str) -> Image.Image:
    """Una pagina del PDF como imagen, ya compuesta sobre blanco.

    `sips` devuelve la pagina con fondo transparente; sin componerla, al pegarla
    en el Word el texto negro queda sobre negro.
    """
    suelta = os.path.join(carpeta, "p%d.pdf" % pagina)
    escritor = pypdf.PdfWriter()
    escritor.add_page(pypdf.PdfReader(PLAN).pages[pagina - 1])
    with open(suelta, "wb") as f:
        escritor.write(f)

    png = os.path.join(carpeta, "p%d.png" % pagina)
    subprocess.run(["sips", "-s", "format", "png", "-s", "formatOptions", "best",
                    "--resampleWidth", str(ANCHO), "--out", png, suelta],
                   capture_output=True)
    cruda = Image.open(png)
    if cruda.mode in ("RGBA", "LA"):
        fondo = Image.new("RGB", cruda.size, "white")
        fondo.paste(cruda, mask=cruda.split()[-1])
        return fondo
    return cruda.convert("RGB")


def titulos_de(pagina: pypdf.PageObject) -> list:
    """Los «Semana N» de la pagina, con su altura en puntos del PDF.

    Devuelve [(numero, y)], contando y desde arriba, que es como se mide la
    imagen. El PDF cuenta desde abajo, asi que se invierte.
    """
    encontrados = []
    alto = float(pagina.mediabox.height)

    def mirar(texto, matriz, tm, fuente, tamano):
        limpio = (texto or "").strip()
        m = TITULO.match(limpio)
        if m:
            encontrados.append((int(m.group(1)), alto - tm[5]))

    pagina.extract_text(visitor_text=mirar)
    return encontrados


def recortar(imagen: Image.Image, desde: int, hasta: int) -> tuple:
    """El rectangulo con tinta dentro de esa franja, mas un poco de aire."""
    franja = imagen.crop((0, desde, imagen.width, hasta)).convert("L")
    caja = ImageOps.invert(franja).getbbox()
    if caja is None:
        return None
    x0, y0, x1, y1 = caja
    return (max(0, x0 - AIRE), max(0, desde + y0 - AIRE),
            min(imagen.width, x1 + AIRE), min(imagen.height, desde + y1 + AIRE))


def main() -> int:
    if not os.path.exists(PLAN):
        print("No encuentro el plan en %s" % PLAN)
        return 1
    os.makedirs(DESTINO, exist_ok=True)
    lector = pypdf.PdfReader(PLAN)

    with tempfile.TemporaryDirectory() as carpeta:
        for numero in range(PRIMERA_PAGINA, len(lector.pages) + 1):
            pagina = lector.pages[numero - 1]
            titulos = titulos_de(pagina)
            if not titulos:
                continue

            imagen = rasterizar(numero, carpeta)
            # El PDF mide en puntos y la imagen en pixeles: la misma pagina en
            # dos escalas. La proporcion convierte de una a la otra.
            escala = imagen.height / float(pagina.mediabox.height)

            for i, (semana, y) in enumerate(titulos):
                arriba = int(y * escala) - RENGLON
                abajo = (int(titulos[i + 1][1] * escala) - RENGLON
                         if i + 1 < len(titulos) else imagen.height)
                caja = recortar(imagen, max(0, arriba), abajo)
                if caja is None:
                    print("semana %d: la franja salio vacia" % semana)
                    continue
                salida = os.path.join(DESTINO, "plan-semana-%d.png" % semana)
                imagen.crop(caja).save(salida, dpi=(200, 200))
                print("semana %-2d  pagina %-2d  %4dx%-4d  %s"
                      % (semana, numero, caja[2] - caja[0], caja[3] - caja[1],
                         os.path.basename(salida)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
