# -*- coding: utf-8 -*-
"""Convierte la salida de una terminal en una imagen para el informe.

No alcanza con pegar el texto en el Word: el informe muestra lo que la persona
ve en la pantalla, y lo que ve son colores sobre fondo oscuro. Se interpretan
las secuencias ANSI --las unicas que usan los scripts son verde, amarillo, rojo
y gris-- y se dibuja con la misma tipografia monoespaciada de la terminal.

    python3 scripts/capturas_terminal.py
"""
from __future__ import annotations

import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, "documento", "img_cierre")

FONDO = (30, 30, 34)
TEXTO = (222, 222, 226)
COLORES = {
    "30": (130, 130, 136), "31": (235, 110, 100), "32": (120, 210, 130),
    "33": (230, 190, 110), "34": (120, 170, 235), "36": (110, 200, 210),
    "90": (130, 130, 136), "0": TEXTO,
}

ESCAPE = re.compile(r"\x1b\[([0-9;]*)m")
CUERPO = 26
INTERLINEA = 38
MARGEN = 28


def tipografia(negrita=False):
    for ruta, indice in (("/System/Library/Fonts/Menlo.ttc", 1 if negrita else 0),
                         ("/System/Library/Fonts/Monaco.dfont", 0)):
        if os.path.exists(ruta):
            try:
                return ImageFont.truetype(ruta, CUERPO, index=indice)
            except OSError:
                continue
    return ImageFont.load_default()


def trozos(linea: str):
    """Parte una linea en pedazos (texto, color) segun las marcas ANSI."""
    salida, color, pos = [], TEXTO, 0
    for marca in ESCAPE.finditer(linea):
        if marca.start() > pos:
            salida.append((linea[pos:marca.start()], color))
        codigos = [c for c in marca.group(1).split(";") if c]
        color = COLORES.get(codigos[-1], TEXTO) if codigos else TEXTO
        pos = marca.end()
    if pos < len(linea):
        salida.append((linea[pos:], color))
    return salida


def dibujar(texto: str, destino: str) -> None:
    lineas = [l.rstrip("\n") for l in texto.split("\n")]
    while lineas and not lineas[-1].strip():
        lineas.pop()

    fuente = tipografia()
    ancho_letra = fuente.getlength("M")
    columnas = max((len(ESCAPE.sub("", l)) for l in lineas), default=1)
    ancho = int(MARGEN * 2 + ancho_letra * max(columnas, 58))
    alto = MARGEN * 2 + INTERLINEA * len(lineas) + 34

    imagen = Image.new("RGB", (ancho, alto), FONDO)
    lapiz = ImageDraw.Draw(imagen)

    # La barra de la ventana, con los tres botones: sin eso la imagen no se
    # lee como una terminal, se lee como un bloque de texto con fondo raro.
    lapiz.rectangle([0, 0, ancho, 34], fill=(48, 48, 54))
    for i, tono in enumerate(((237, 106, 94), (244, 191, 79), (98, 197, 84))):
        cx = 20 + i * 20
        lapiz.ellipse([cx - 6, 11, cx + 6, 23], fill=tono)

    y = 34 + MARGEN
    for linea in lineas:
        x = MARGEN
        for pedazo, color in trozos(linea):
            lapiz.text((x, y), pedazo, font=fuente, fill=color)
            x += fuente.getlength(pedazo)
        y += INTERLINEA

    imagen.save(destino)
    print("  %s  (%d x %d)" % (os.path.basename(destino), ancho, alto))


def main() -> int:
    if len(sys.argv) > 1:
        origen, nombre = sys.argv[1], sys.argv[2]
        with open(origen, encoding="utf-8") as f:
            dibujar(f.read(), os.path.join(SALIDA, nombre))
        return 0
    print("uso: capturas_terminal.py <archivo.txt> <salida.png>")
    return 1


if __name__ == "__main__":
    sys.exit(main())
