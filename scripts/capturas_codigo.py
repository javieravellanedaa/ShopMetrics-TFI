# -*- coding: utf-8 -*-
"""Rasteriza el codigo de cada script como figura para el informe.

El recorte no es arbitrario: se toma el encabezado del archivo --la cabecera
que explica que resuelve y contra que caso de uso-- mas las primeras lineas de
codigo, hasta completar el alto que entra en una figura de A4. Un listado
completo de trescientas lineas no se lee en papel; el encabezado y lo que sigue,
si.

    python3 scripts/capturas_codigo.py            todos
    python3 scripts/capturas_codigo.py api/app/cifrado.py
"""
from __future__ import annotations

import os
import sys

from pygments import highlight
from pygments.formatters import ImageFormatter
from pygments.lexers import get_lexer_for_filename, TextLexer
from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODIGO = os.path.join(os.path.dirname(RAIZ), "shopmetrics")
DESTINO = os.path.join(RAIZ, "documento", "img_cierre")

MONO = "/System/Library/Fonts/Menlo.ttc"
SANS = "/System/Library/Fonts/Supplemental/Arial.ttf"

# Veintiseis lineas alcanzan para el encabezado del archivo y las primeras
# definiciones. Con mas, la figura sale casi cuadrada y al escalarla al ancho de
# la pagina ocupa media hoja: Word la empuja a la pagina siguiente y deja el
# hueco en blanco.
LINEAS = 26
TAMANO = 15             # cuerpo del monoespaciado al rasterizar
BARRA = 34              # alto de la barra con el nombre del archivo


def _recorte(texto: str, cuantas: int) -> tuple:
    """Las primeras lineas utiles del archivo. Devuelve (texto, total, cortado).

    Se saltean las lineas en blanco del principio y el `# -*- coding` para no
    gastar renglones de la figura en algo que no dice nada.
    """
    lineas = texto.splitlines()
    total = len(lineas)
    arranque = 0
    while arranque < total and (not lineas[arranque].strip()
                                or lineas[arranque].startswith("# -*-")):
        arranque += 1
    elegidas = lineas[arranque:arranque + cuantas]
    return "\n".join(elegidas), total, (arranque + cuantas) < total


def rasterizar(relativo: str, cuantas: int = LINEAS) -> str:
    """Genera la figura del archivo y devuelve la ruta del PNG."""
    ruta = os.path.join(CODIGO, relativo)
    if not os.path.exists(ruta):
        raise FileNotFoundError(relativo)

    crudo = open(ruta, encoding="utf-8").read()
    fragmento, total, cortado = _recorte(crudo, cuantas)

    try:
        lexer = get_lexer_for_filename(relativo, stripnl=False)
    except Exception:
        lexer = TextLexer()

    formato = ImageFormatter(
        font_name="Menlo", font_size=TAMANO, line_numbers=True,
        line_number_bg="#f0f0f4", line_number_fg="#9a9aa8",
        line_number_separator=False, line_number_pad=8,
        style="friendly", image_pad=14)
    png = os.path.join(DESTINO, "codigo-%s.png"
                       % relativo.replace("/", "-").replace(".", "_"))
    with open(png, "wb") as f:
        f.write(highlight(fragmento, lexer, formato))

    _ponerle_barra(png, relativo, total, cortado, cuantas)
    return png


def _ponerle_barra(png: str, relativo: str, total: int, cortado: bool,
                   cuantas: int) -> None:
    """Le agrega arriba una barra con el nombre del archivo, como un editor.

    Sin el nombre, una figura de codigo es un bloque de texto sin contexto: hay
    que poder decir de que archivo se esta mirando sin bajar hasta el epigrafe.
    """
    cuerpo = Image.open(png).convert("RGB")
    ancho = cuerpo.width
    lienzo = Image.new("RGB", (ancho, cuerpo.height + BARRA), "#ffffff")
    pincel = ImageDraw.Draw(lienzo)
    pincel.rectangle([0, 0, ancho, BARRA], fill="#1E1B4B")

    try:
        letra = ImageFont.truetype(MONO, 15)
        letrita = ImageFont.truetype(SANS, 13)
    except OSError:
        letra = letrita = ImageFont.load_default()

    pincel.text((14, BARRA // 2), relativo, font=letra, fill="#ffffff", anchor="lm")
    derecha = ("líneas 1 a %d de %d" % (cuantas, total)) if cortado \
        else ("%d líneas" % total)
    pincel.text((ancho - 14, BARRA // 2), derecha, font=letrita,
                fill="#b9b6e0", anchor="rm")

    lienzo.paste(cuerpo, (0, BARRA))
    pincel.rectangle([0, 0, ancho - 1, lienzo.height - 1], outline="#d0d0da")
    lienzo.save(png, dpi=(200, 200))


def main() -> int:
    os.makedirs(DESTINO, exist_ok=True)
    sys.path.insert(0, os.path.join(CODIGO, "herramientas"))
    from fichas import TARJETAS                      # noqa: E402

    pedidos = sys.argv[1:]
    if pedidos:
        archivos = pedidos
    else:
        # Todos los scripts de todas las tarjetas, sin repetir y en orden.
        vistos, archivos = set(), []
        for _, ficha in sorted(TARJETAS.items()):
            for archivo, _, _ in ficha["archivos"]:
                if archivo not in vistos and _es_script(archivo):
                    vistos.add(archivo)
                    archivos.append(archivo)

    for archivo in archivos:
        try:
            png = rasterizar(archivo)
        except FileNotFoundError:
            print("  falta %s" % archivo)
            continue
        alto = Image.open(png).height
        print("  %-52s -> %s (%d px de alto)"
              % (archivo, os.path.basename(png), alto))
    print("\n%d figuras en %s" % (len(archivos), DESTINO))
    return 0


def _es_script(archivo: str) -> bool:
    """Si vale la pena mostrarlo como codigo.

    Un `.env.ejemplo` o un `package.json` no aportan nada como figura: son
    listas de valores, no logica que se pueda leer.
    """
    return archivo.endswith((".py", ".sql", ".ts", ".tsx", ".sh", ".css"))


if __name__ == "__main__":
    sys.exit(main())
