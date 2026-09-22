# -*- coding: utf-8 -*-
"""Arma el video del recorrido de punta a punta, con los rotulos encima.

Cada captura se convierte en un cuadro de 1920x1080 con tres partes: arriba el
caso de uso, en el medio la pantalla y abajo lo que la persona tiene que hacer.
Entre caso y caso se intercala una placa.

El video no se graba: se compone. Grabar la pantalla mientras se maneja el
navegador da un archivo lleno de esperas, punteros que titubean y momentos en
que no pasa nada. Componerlo desde capturas deja cada pantalla el tiempo que
hace falta para leerla y nada mas.

    python3 scripts/armar_video.py
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CUADROS = os.path.join(RAIZ, "documento", "img_video")
SALIDA = os.path.join(RAIZ, "documento", "ShopMetrics-recorrido.mp4")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guion_video import CASOS, PASOS            # noqa: E402

ANCHO, ALTO = 1920, 1080
CUADROS_POR_SEGUNDO = 30

# El reparto vertical del cuadro.
BARRA = 96                  # la franja de arriba, con el caso de uso
PIE = 232                   # la de abajo, con la instruccion
MARGEN = 36

# La paleta del sistema, para que el video se vea de la misma familia.
VIOLETA_OSCURO = (30, 27, 75)
VIOLETA = (79, 63, 199)
BLANCO = (255, 255, 255)
LILA = (185, 182, 224)
PAPEL = (244, 244, 247)
TINTA = (34, 34, 34)
TINTA_SUAVE = (110, 110, 125)
AMBAR = (245, 158, 11)

FUENTES = "/System/Library/Fonts/Supplemental"


def letra(nombre: str, tamano: int):
    try:
        return ImageFont.truetype(os.path.join(FUENTES, nombre), tamano)
    except OSError:
        return ImageFont.load_default()


NEGRITA = lambda t: letra("Arial Bold.ttf", t)          # noqa: E731
NORMAL = lambda t: letra("Arial.ttf", t)                # noqa: E731
CURSIVA = lambda t: letra("Arial Italic.ttf", t)        # noqa: E731


def partir(texto: str, fuente, ancho: int) -> list:
    """Corta el texto en renglones que entren en ese ancho."""
    palabras, renglones, actual = texto.split(), [], ""
    medir = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    for palabra in palabras:
        prueba = (actual + " " + palabra).strip()
        if medir.textlength(prueba, font=fuente) <= ancho:
            actual = prueba
        else:
            if actual:
                renglones.append(actual)
            actual = palabra
    if actual:
        renglones.append(actual)
    return renglones


def placa(codigo: str, caso: dict, numero: int, total: int) -> Image.Image:
    """La portada de cada caso de uso."""
    lienzo = Image.new("RGB", (ANCHO, ALTO), VIOLETA_OSCURO)
    pincel = ImageDraw.Draw(lienzo)

    pincel.text((ANCHO // 2, 356), "Caso de uso %d de %d" % (numero, total),
                font=NORMAL(30), fill=LILA, anchor="mm")
    pincel.text((ANCHO // 2, 430), codigo, font=NEGRITA(88), fill=BLANCO, anchor="mm")

    y = 540
    for renglon in partir(caso["nombre"], NEGRITA(46), ANCHO - 400):
        pincel.text((ANCHO // 2, y), renglon, font=NEGRITA(46), fill=BLANCO, anchor="mm")
        y += 60

    y += 24
    for renglon in partir(caso["resumen"], NORMAL(30), ANCHO - 520):
        pincel.text((ANCHO // 2, y), renglon, font=NORMAL(30), fill=LILA, anchor="mm")
        y += 44

    pincel.line([(ANCHO // 2 - 60, 494), (ANCHO // 2 + 60, 494)], fill=VIOLETA, width=4)
    return lienzo


def cuadro(archivo: str, codigo: str, titulo: str, detalle: str,
           nota: str, paso: int, total: int) -> Image.Image:
    """Un paso: la captura con su rotulo arriba y su instruccion abajo."""
    lienzo = Image.new("RGB", (ANCHO, ALTO), PAPEL)
    pincel = ImageDraw.Draw(lienzo)

    # --- la franja de arriba
    pincel.rectangle([0, 0, ANCHO, BARRA], fill=VIOLETA_OSCURO)
    pincel.text((MARGEN + 8, BARRA // 2), codigo, font=NEGRITA(34),
                fill=BLANCO, anchor="lm")
    ancho_codigo = pincel.textlength(codigo, font=NEGRITA(34))
    pincel.text((MARGEN + 28 + ancho_codigo, BARRA // 2), CASOS[codigo]["nombre"],
                font=NORMAL(28), fill=LILA, anchor="lm")
    pincel.text((ANCHO - MARGEN - 8, BARRA // 2), "Paso %d de %d" % (paso, total),
                font=NORMAL(26), fill=LILA, anchor="rm")

    # --- la captura, centrada en el espacio que queda
    alto_util = ALTO - BARRA - PIE
    imagen = Image.open(os.path.join(CUADROS, archivo + ".jpg")).convert("RGB")
    escala = min((ANCHO - MARGEN * 2) / imagen.width, alto_util / imagen.height)
    nuevo = imagen.resize((int(imagen.width * escala), int(imagen.height * escala)),
                          Image.LANCZOS)
    x = (ANCHO - nuevo.width) // 2
    y = BARRA + (alto_util - nuevo.height) // 2
    # Un borde fino para que la captura no se funda con el fondo del cuadro.
    pincel.rectangle([x - 1, y - 1, x + nuevo.width, y + nuevo.height],
                     outline=(210, 210, 220))
    lienzo.paste(nuevo, (x, y))

    # --- la franja de abajo
    arriba_del_pie = ALTO - PIE
    pincel.rectangle([0, arriba_del_pie, ANCHO, ALTO], fill=BLANCO)
    pincel.line([(0, arriba_del_pie), (ANCHO, arriba_del_pie)], fill=(215, 215, 225))
    pincel.rectangle([0, arriba_del_pie, 8, ALTO], fill=VIOLETA)

    cursor = arriba_del_pie + 30
    pincel.text((MARGEN + 16, cursor), titulo, font=NEGRITA(38), fill=TINTA, anchor="lt")
    cursor += 54
    for renglon in partir(detalle, NORMAL(27), ANCHO - MARGEN * 2 - 40):
        pincel.text((MARGEN + 16, cursor), renglon, font=NORMAL(27),
                    fill=(70, 70, 82), anchor="lt")
        cursor += 36

    if nota:
        cursor += 6
        for renglon in partir("· " + nota, CURSIVA(24), ANCHO - MARGEN * 2 - 40):
            pincel.text((MARGEN + 16, cursor), renglon, font=CURSIVA(24),
                        fill=TINTA_SUAVE, anchor="lt")
            cursor += 32

    # --- la barra de avance
    ancho_barra = int((ANCHO - MARGEN * 2) * paso / total)
    pincel.rectangle([MARGEN, ALTO - 12, ANCHO - MARGEN, ALTO - 8], fill=(226, 226, 236))
    pincel.rectangle([MARGEN, ALTO - 12, MARGEN + ancho_barra, ALTO - 8], fill=VIOLETA)
    return lienzo


def portada() -> Image.Image:
    lienzo = Image.new("RGB", (ANCHO, ALTO), VIOLETA_OSCURO)
    pincel = ImageDraw.Draw(lienzo)
    pincel.text((ANCHO // 2, 372), "ShopMetrics", font=NEGRITA(96),
                fill=BLANCO, anchor="mm")
    pincel.text((ANCHO // 2, 462), "Recorrido del sistema de punta a punta",
                font=NORMAL(40), fill=LILA, anchor="mm")
    pincel.line([(ANCHO // 2 - 90, 524), (ANCHO // 2 + 90, 524)], fill=VIOLETA, width=4)
    pincel.text((ANCHO // 2, 588),
                "Siete casos de uso, veintiún pasos, sobre el sistema funcionando",
                font=NORMAL(30), fill=LILA, anchor="mm")
    pincel.text((ANCHO // 2, 700), "Javier Gómez Avellaneda",
                font=NORMAL(30), fill=BLANCO, anchor="mm")
    pincel.text((ANCHO // 2, 744), "Trabajo Final de Ingeniería · UAI",
                font=NORMAL(26), fill=LILA, anchor="mm")
    return lienzo


def cierre() -> Image.Image:
    lienzo = Image.new("RGB", (ANCHO, ALTO), VIOLETA_OSCURO)
    pincel = ImageDraw.Draw(lienzo)
    pincel.text((ANCHO // 2, 396), "Todo lo que se vio corre de verdad",
                font=NEGRITA(52), fill=BLANCO, anchor="mm")
    y = 492
    for renglon in ("Base de datos PostgreSQL con TimescaleDB, la API, el panel web,",
                    "los dos simuladores de sistemas externos y el generador de datos.",
                    "",
                    "Ningún número de este video está escrito en la pantalla:",
                    "todos salen de la base."):
        pincel.text((ANCHO // 2, y), renglon, font=NORMAL(30), fill=LILA, anchor="mm")
        y += 46
    return lienzo


def main() -> int:
    if shutil.which("ffmpeg") is None:
        print("Falta ffmpeg.")
        return 1

    total = len(PASOS)
    codigos = []
    for _, codigo, _, _, _ in PASOS:
        if codigo not in codigos:
            codigos.append(codigo)

    with tempfile.TemporaryDirectory() as carpeta:
        n = 0
        lista = []

        def guardar(imagen, segundos):
            nonlocal n
            n += 1
            ruta = os.path.join(carpeta, "c%04d.png" % n)
            imagen.save(ruta)
            lista.append((ruta, segundos))

        guardar(portada(), 4.5)

        visto = set()
        for i, (archivo, codigo, titulo, detalle, nota) in enumerate(PASOS, 1):
            if codigo not in visto:
                visto.add(codigo)
                guardar(placa(codigo, CASOS[codigo], codigos.index(codigo) + 1,
                              len(codigos)), 3.5)
            # Cuanto dura el paso: lo que se tarda en leerlo, con un piso.
            palabras = len((titulo + " " + detalle + " " + (nota or "")).split())
            segundos = max(5.0, min(11.0, 2.6 + palabras / 3.1))
            guardar(cuadro(archivo, codigo, titulo, detalle, nota, i, total), segundos)

        guardar(cierre(), 5.0)

        # El archivo de concatenacion de ffmpeg. La ultima imagen se repite
        # porque el demuxer ignora la duracion del ultimo elemento.
        guion = os.path.join(carpeta, "guion.txt")
        with open(guion, "w", encoding="utf-8") as f:
            for ruta, segundos in lista:
                f.write("file '%s'\nduration %.2f\n" % (ruta, segundos))
            f.write("file '%s'\n" % lista[-1][0])

        orden = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", guion,
                 "-vf", "fps=%d,format=yuv420p" % CUADROS_POR_SEGUNDO,
                 "-c:v", "libx264", "-preset", "slow", "-crf", "20",
                 "-movflags", "+faststart", SALIDA]
        r = subprocess.run(orden, capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stderr[-1500:])
            return 1

    duracion = sum(s for _, s in lista)
    print("video: %s" % SALIDA)
    print("  %d cuadros · %d min %02d s · %.1f MB"
          % (len(lista), int(duracion // 60), int(duracion % 60),
             os.path.getsize(SALIDA) / 1e6))
    return 0


if __name__ == "__main__":
    sys.exit(main())
