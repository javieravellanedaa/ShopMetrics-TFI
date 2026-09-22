# -*- coding: utf-8 -*-
"""Arma el informe de construccion con el formato de la catedra.

El formato no se reconstruye: se parte del propio Word del trabajo final, se le
vacia el cuerpo y se escribe encima. Asi el documento hereda exactamente los
mismos estilos, el mismo encabezado con el escudo de la Universidad, los mismos
margenes y la misma tipografia, sin tener que replicar nada a mano.

    python3 scripts/armar_cierre.py
"""
from __future__ import annotations

import os
import shutil
import sys
from datetime import date

import docx
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Mm, Pt, RGBColor
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODIGO = os.path.join(os.path.dirname(RAIZ), "shopmetrics")
PLANTILLA = os.path.join(RAIZ, "documento", "STF_Gomez_Javier_E1_v1.docx")
IMAGENES = os.path.join(RAIZ, "documento", "img_cierre")
CAPTURAS = os.path.join(RAIZ, "documento", "img_video")
SALIDA = os.path.join(RAIZ, "documento", "STF_Gomez_Javier_Construccion.docx")

sys.path.insert(0, os.path.join(CODIGO, "herramientas"))
from fichas import (COMMITS, REPO, SEMANA_DE_COMMIT, SEMANAS,  # noqa: E402
                    TARJETAS)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guion_video import CASOS, PASOS  # noqa: E402

# El ancho util de la pagina es 162,5 mm --A4 menos los margenes-- pero las
# figuras se dejan en 159: a ancho exacto, el redondeo del renderizador recorta
# un par de milimetros por la derecha y se come el final de cada linea de codigo.
ANCHO_UTIL_MM = 159.0

MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre")


# --------------------------------------------------------------- utilidades

def vaciar(documento) -> None:
    """Deja el documento sin contenido pero con sus estilos y su encabezado.

    Se conserva el ultimo `sectPr`, que es el que define el tamano de pagina,
    los margenes y de que encabezado cuelga la seccion. Sacarlo dejaria el
    documento sin formato de pagina.
    """
    cuerpo = documento.element.body
    ultimo = cuerpo.find(qn("w:sectPr"))
    for hijo in list(cuerpo):
        if hijo is not ultimo:
            cuerpo.remove(hijo)


def enlace(parrafo, texto: str, url: str) -> None:
    """Un hipervinculo de verdad, de los que se pueden clickear en el Word."""
    parte = parrafo.part
    ident = parte.relate_to(
        url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True)
    nodo = OxmlElement("w:hyperlink")
    nodo.set(qn("r:id"), ident)
    tirada = OxmlElement("w:r")
    props = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "1155CC")
    subrayado = OxmlElement("w:u")
    subrayado.set(qn("w:val"), "single")
    props.append(color)
    props.append(subrayado)
    tirada.append(props)
    nodo_texto = OxmlElement("w:t")
    nodo_texto.text = texto
    tirada.append(nodo_texto)
    nodo.append(tirada)
    parrafo._p.append(nodo)


def parrafo(documento, texto="", estilo=None, tamano=None, negrita=False,
            cursiva=False, color=None, alineacion=None, antes=None, despues=None):
    p = documento.add_paragraph(style=estilo)
    if texto:
        t = p.add_run(texto)
        t.bold = negrita
        t.italic = cursiva
        if tamano:
            t.font.size = Pt(tamano)
        if color:
            t.font.color.rgb = RGBColor.from_string(color)
    if alineacion is not None:
        p.alignment = alineacion
    if antes is not None:
        p.paragraph_format.space_before = Pt(antes)
    if despues is not None:
        p.paragraph_format.space_after = Pt(despues)
    return p


def sin_cortar(fila) -> None:
    """Impide que Word parta la fila entre dos paginas."""
    props = fila._tr.get_or_add_trPr()
    marca = OxmlElement("w:cantSplit")
    props.append(marca)


def figura(documento, archivo: str, epigrafe: str, ancho_mm=None,
           alto_maximo_mm=None, carpeta=None) -> bool:
    """Pega una imagen con su epigrafe, sin que se separen ni se desborden.

    La imagen y su epigrafe van dentro de una tabla de una sola celda que no se
    puede partir: sin eso, Word manda el epigrafe solo a la pagina siguiente y
    queda huerfano de su figura.
    """
    ruta = os.path.join(carpeta or IMAGENES, archivo)
    if not os.path.exists(ruta):
        print("    falta la imagen %s" % archivo)
        return False

    ancho_px, alto_px = Image.open(ruta).size
    ancho = ancho_mm or ANCHO_UTIL_MM
    alto = ancho * alto_px / ancho_px
    if alto_maximo_mm and alto > alto_maximo_mm:
        alto = alto_maximo_mm
        ancho = alto * ancho_px / alto_px

    tabla = documento.add_table(rows=1, cols=1)
    tabla.autofit = False
    sin_cortar(tabla.rows[0])
    celda = tabla.cell(0, 0)
    # La celda tiene que ser al menos tan ancha como la figura: si queda mas
    # angosta, Word no la achica, la recorta por la derecha y se pierde el final
    # de cada linea de codigo sin que nada avise.
    celda.width = Mm(ANCHO_UTIL_MM)
    _sin_margenes(celda)
    celda.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    celda.paragraphs[0].add_run().add_picture(ruta, width=Mm(ancho), height=Mm(alto))
    pie = celda.add_paragraph(epigrafe, style="Epígrafe de figura")
    pie.paragraph_format.space_before = Pt(4)
    return True


def tabla_de(documento, encabezados, filas, anchos_mm=None, epigrafe=None):
    """Una tabla con la primera fila en negrita y bordes finos."""
    t = documento.add_table(rows=1, cols=len(encabezados))
    t.style = "Table Grid"
    if anchos_mm:
        # Sin diseño fijo, Word reparte las columnas por su contenido y los
        # anchos que se piden quedan de adorno: una columna de números termina
        # ocupando media tabla.
        _ancho_fijo(t)
    for i, texto in enumerate(encabezados):
        celda = t.rows[0].cells[i]
        celda.text = ""
        tirada = celda.paragraphs[0].add_run(texto)
        tirada.bold = True
        tirada.font.size = Pt(9)
        _sombrear(celda, "F1F1F5")
    for fila in filas:
        nueva = t.add_row()
        sin_cortar(nueva)
        for i, valor in enumerate(fila):
            celda = nueva.cells[i]
            celda.text = ""
            p = celda.paragraphs[0]
            if isinstance(valor, tuple):            # (texto, url)
                enlace(p, valor[0], valor[1])
                for r in p.runs:
                    r.font.size = Pt(9)
            else:
                r = p.add_run(str(valor))
                r.font.size = Pt(9)
    if anchos_mm:
        for fila in t.rows:
            for i, ancho in enumerate(anchos_mm):
                fila.cells[i].width = Mm(ancho)
        for i, ancho in enumerate(anchos_mm):
            t.columns[i].width = Mm(ancho)
    if epigrafe:
        p = documento.add_paragraph(epigrafe, style="Epígrafe de tabla")
        p.paragraph_format.space_before = Pt(3)
    return t


def _ancho_fijo(tabla) -> None:
    """Le dice a Word que respete los anchos declarados y no los recalcule."""
    props = tabla._tbl.tblPr
    diseno = OxmlElement("w:tblLayout")
    diseno.set(qn("w:type"), "fixed")
    props.append(diseno)


def _sin_margenes(celda) -> None:
    """Saca el relleno interno de la celda, que le roba ancho a la figura."""
    props = celda._tc.get_or_add_tcPr()
    margenes = OxmlElement("w:tcMar")
    for lado in ("top", "start", "bottom", "end"):
        nodo = OxmlElement("w:%s" % lado)
        nodo.set(qn("w:w"), "0")
        nodo.set(qn("w:type"), "dxa")
        margenes.append(nodo)
    props.append(margenes)


def _sombrear(celda, color: str) -> None:
    props = celda._tc.get_or_add_tcPr()
    relleno = OxmlElement("w:shd")
    relleno.set(qn("w:val"), "clear")
    relleno.set(qn("w:fill"), color)
    props.append(relleno)


def salto(documento) -> None:
    documento.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def vineta(documento, texto: str):
    """Un item de lista.

    La plantilla no trae estilo de viñeta: el documento original arma las listas
    con numeracion de Word, que habria que definir a mano. Se usa `List
    Paragraph`, que si existe y ya viene con la sangria, mas el caracter de
    viñeta.
    """
    p = documento.add_paragraph(style="List Paragraph")
    p.paragraph_format.space_after = Pt(3)
    p.add_run("•  ")
    p.add_run(texto)
    return p


# ------------------------------------------------------------- el documento

def poner_al_dia_encabezado(d) -> None:
    """Cambia la fecha del encabezado y el rotulo del pie.

    El encabezado y el pie vienen de la entrega anterior porque el documento se
    arma sobre ese archivo. Los datos de la catedra --el escudo, la facultad, la
    comision-- se conservan; lo que cambia es de que entrega se trata.
    """
    hoy = date.today()
    for seccion in d.sections:
        for tabla in seccion.header.tables:
            for fila in tabla.rows:
                for celda in fila.cells:
                    if "Fecha" in celda.text and "/" in celda.text:
                        _reescribir(celda.paragraphs[-1],
                                    hoy.strftime("%d/%m/%Y"))
        for tabla in seccion.footer.tables:
            for fila in tabla.rows:
                for celda in fila.cells:
                    if "Entrega Final" in celda.text:
                        _reescribir(celda.paragraphs[0],
                                    "Informe de construcción del sistema · "
                                    "Semanas 1 a 6")


def _reescribir(parrafo, texto: str) -> None:
    """Cambia el texto conservando el formato de la primera tirada."""
    if not parrafo.runs:
        parrafo.add_run(texto)
        return
    parrafo.runs[0].text = texto
    for sobrante in parrafo.runs[1:]:
        sobrante.text = ""


def portada(d) -> None:
    for _ in range(4):
        parrafo(d)
    parrafo(d, "Universidad Abierta Interamericana", tamano=13,
            alineacion=WD_ALIGN_PARAGRAPH.CENTER, despues=2)
    parrafo(d, "Facultad de Tecnología Informática", tamano=13,
            alineacion=WD_ALIGN_PARAGRAPH.CENTER, despues=30)

    parrafo(d, "ShopMetrics", tamano=30, negrita=True,
            alineacion=WD_ALIGN_PARAGRAPH.CENTER, despues=4)
    parrafo(d, "Informe de construcción del sistema", tamano=17,
            alineacion=WD_ALIGN_PARAGRAPH.CENTER, color="434343", despues=4)
    parrafo(d, "Semanas 1 a 6 del plan de trabajo", tamano=13, cursiva=True,
            alineacion=WD_ALIGN_PARAGRAPH.CENTER, color="666666", despues=40)

    hoy = date.today()
    datos = [("Alumno", "Javier Gómez Avellaneda"),
             ("Legajo", "B00074234-T1"),
             ("Carrera", "Ingeniería en Sistemas Informáticos"),
             ("Asignatura", "Seminario de Trabajo Final"),
             ("Comisión", "5.º A — Turno Noche"),
             ("Sede", "Centro"),
             ("Fecha", "%d de %s de %d" % (hoy.day, MESES[hoy.month - 1], hoy.year))]
    t = d.add_table(rows=0, cols=2)
    for rotulo, valor in datos:
        fila = t.add_row()
        izq = fila.cells[0].paragraphs[0].add_run(rotulo)
        izq.bold = True
        izq.font.size = Pt(11)
        fila.cells[1].paragraphs[0].add_run(valor).font.size = Pt(11)
        fila.cells[0].width = Mm(45)
        fila.cells[1].width = Mm(117)
    salto(d)


def introduccion(d) -> None:
    d.add_paragraph("1. Sobre este informe", style="Heading 1")

    parrafo(d, "Este informe documenta la construcción del sistema ShopMetrics "
               "durante las primeras seis semanas del plan de trabajo presentado "
               "en la entrega anterior. No reemplaza a ese plan ni al documento "
               "de análisis y diseño: los toma como punto de partida y da cuenta "
               "de qué se construyó efectivamente contra cada tarea comprometida.")

    parrafo(d, "Cada semana ocupa un capítulo y cada tarea de esa semana, un "
               "apartado. Para cada tarea se deja constancia de seis cosas: el "
               "texto literal de la tarea en el plan de trabajo, lo que se hizo "
               "paso a paso, los archivos que quedaron escritos, las pruebas que "
               "los cubren, los commits que hicieron el trabajo y la tarjeta del "
               "tablero donde vive su seguimiento.")

    parrafo(d, "Los enlaces a los archivos no apuntan a la rama principal sino al "
               "commit exacto donde mirarlos. La diferencia importa: la rama "
               "principal sigue avanzando y en unos meses mostraría algo distinto "
               "de lo que este informe describe, mientras que un enlace fijado a "
               "un commit muestra siempre el mismo código.")

    d.add_paragraph("1.1 Cómo se verifica lo que dice este informe", style="Heading 2")
    parrafo(d, "Todo lo que sigue es reproducible desde el repositorio. Con Docker "
               "levantado, estos cuatro comandos reconstruyen el entorno desde "
               "cero, corren las pruebas de los dos lados y verifican que el "
               "código, el esquema de la base y el documento de análisis digan lo "
               "mismo:")
    for orden, que in (("make limpiar && make arriba", "rehace la base desde las migraciones"),
                       ("make probar", "las pruebas de la API"),
                       ("make probar-panel", "las pruebas del panel"),
                       ("make nivelar", "cruza documento, esquema y código")):
        p = parrafo(d, "", despues=2)
        t = p.add_run(orden)
        t.font.name = "Menlo"
        t.font.size = Pt(10)
        p.add_run("   " + que).font.size = Pt(10)

    d.add_paragraph("1.2 Criterio para dar una tarea por terminada", style="Heading 2")
    parrafo(d, "Una tarea se cierra cuando cumple cuatro condiciones, no sólo la "
               "primera: el código está escrito y subido; hay pruebas que cubren "
               "todos los escenarios y no únicamente el que sale bien —cada curso "
               "alternativo de la especificación, cada validación por su propio "
               "motivo, los permisos y los límites—; la tarjeta del tablero tiene "
               "la evidencia con enlaces permanentes; y el control de nivelación "
               "contra el documento está en verde.")
    salto(d)


def resumen(d) -> None:
    d.add_paragraph("2. Resumen de lo construido", style="Heading 1")

    parrafo(d, "Las seis semanas produjeron un backend, un panel web, dos "
               "simuladores de sistemas externos y un generador de datos, además "
               "de las herramientas de verificación que sostienen el resto.")

    nacidas = _pruebas_por_semana()
    filas, acumulado = [], 0
    for numero in sorted(SEMANAS):
        tarjetas = [t for t in TARJETAS.values() if t["semana"] == numero]
        archivos = {a for t in tarjetas for a, _, _ in t["archivos"]}
        acumulado += nacidas.get(numero, 0)
        filas.append((str(numero),
                      SEMANAS[numero]["titulo"].split("· ")[1],
                      str(len(tarjetas)),
                      str(len(archivos)),
                      str(nacidas.get(numero, 0)),
                      str(acumulado)))
    tabla_de(d, ["Semana", "Tema", "Tareas", "Archivos", "Pruebas nuevas",
                 "Acumulado"], filas,
             anchos_mm=[19, 53, 17, 21, 26, 23],
             epigrafe="Tabla 1. Alcance construido por semana. Las pruebas se "
                      "cuentan en la semana en que nació el archivo que las "
                      "contiene. Fuente: elaboración propia.")

    parrafo(d, "", despues=6)
    parrafo(d, "La columna de archivos cuenta los que cada semana tocó, no sólo "
               "los que creó: un mismo archivo puede aparecer en varias semanas "
               "porque se lo siguió trabajando. Las pruebas, en cambio, se "
               "cuentan una sola vez, en la semana en que apareció el archivo "
               "que las contiene, y por eso sí suman.", tamano=10, cursiva=True)

    d.add_paragraph("2.1 Casos de uso construidos", style="Heading 2")
    parrafo(d, "De los 31 casos de uso especificados en el punto 10.5.3 del "
               "documento de análisis, diez tienen endpoints construidos y "
               "verificados. Cada endpoint cita en su documentación el caso de "
               "uso que materializa, de modo que la documentación que genera la "
               "API es también la trazabilidad contra el informe.")
    casos = [
        ("CU-001", "Monitorear estado de las integraciones", "4"),
        ("CU-002", "Registrar conector POS de un locatario", "3"),
        ("CU-003", "Registrar dispositivo IoT de conteo", "3"),
        ("CU-004", "Consultar mapa del centro y zonas", "4"),
        ("CU-006", "Configurar alerta basada en umbral", "6"),
        ("CU-007", "Recibir y gestionar alerta generada", "6"),
        ("CU-011", "Consultar dashboard general y KPIs", "4"),
        ("CU-017", "Autenticarse en la plataforma", "2"),
        ("CU-018", "Configurar permisos granulares", "2"),
        ("CU-026", "Monitorear centro de alertas críticas", "6"),
    ]
    tabla_de(d, ["Caso de uso", "Nombre", "Semana"], casos,
             anchos_mm=[28, 105, 26],
             epigrafe="Tabla 2. Casos de uso con endpoints construidos. "
                      "Fuente: elaboración propia sobre el punto 10.5.3.")
    salto(d)


# Que pantallas mostrar en cada tarjeta, para las que tienen interfaz.
PANTALLAS = {
    14: [("ui-ingresar.jpg", "Pantalla de ingreso. El destino posterior lo "
                             "decide el backend, no esta pantalla.")],
    15: [("ui-panel-inicio.jpg", "Tablero de indicadores. Los cuatro valores y "
                                 "la serie por hora vienen de la API."),
         ("ui-mapa-centro.jpg", "Mapa del centro, con el semáforo de cobertura "
                                "por zona."),
         ("ui-integraciones.jpg", "Salud de las integraciones, con la última "
                                  "sincronización de cada fuente.")],
    16: [("ui-celular.jpg", "Las mismas pantallas a 390 píxeles de ancho: el "
                            "menú pasa a barra horizontal y los indicadores se "
                            "apilan. No hay una versión móvil aparte.")],
    19: [("ui-alertas.jpg", "Centro de alertas, ordenado por severidad y con "
                            "los filtros del paso 4."),
         ("ui-alertas-ficha.jpg", "La ficha al costado de la lista: detalle, "
                                  "SLA, asignación y checklist guiado."),
         ("ui-reglas.jpg", "Configuración de reglas. Debajo del indicador se "
                           "muestran sus rangos típicos del último mes.")],
}

# Cuantas figuras de codigo mostrar por tarjeta. Mostrarlas todas haria un
# documento de doscientas paginas; se eligen las que explican la decision.
CODIGO_DESTACADO = {
    1: ["docker-compose.yml", "base/inicializar.sh"],
    2: ["base/generar_esquema.py", "api/nivelacion.py"],
    3: ["herramientas/evidencia.py"],
    4: ["api/app/main.py"],
    5: ["api/app/seguridad.py"],
    6: ["api/app/dependencias.py"],
    7: ["api/pruebas/conftest_postgres.py"],
    8: ["api/app/cifrado.py", "api/app/dominios/integraciones/sincronizador.py",
        "simuladores/pos/main.py"],
    9: ["simuladores/iot/main.py", "simuladores/pos/trafico.py"],
    10: ["generador/correr.py", "generador/carga.py"],
    11: ["api/app/dominios/integraciones/salud.py", "api/app/tareas.py"],
    12: ["api/app/dominios/metricas/servicio.py",
         "api/app/dominios/metricas/consultas.py"],
    13: ["base/migraciones/003_agregados.sql"],
    14: ["web/servicios/api.ts", "web/componentes/Menu.tsx"],
    15: ["web/app/panel/page.tsx", "web/componentes/GraficoDeBarras.tsx"],
    16: ["web/app/globales.css"],
    17: ["api/app/dominios/alertas/reglas.py", "api/app/dominios/alertas/motor.py"],
    18: ["api/app/dominios/alertas/ciclo.py",
         "base/migraciones/004_alerta_opcionales.sql"],
    19: ["web/app/panel/alertas/page.tsx", "web/componentes/FichaDeAlerta.tsx"],
}


def _nombre_figura(archivo: str) -> str:
    return "codigo-%s.png" % archivo.replace("/", "-").replace(".", "_")


def _pruebas_por_semana() -> dict:
    """Cuantas pruebas nacieron en cada semana, segun el historial del repositorio.

    No se declara a mano: se le pregunta a git que commit agrego cada archivo de
    pruebas y se lo lleva a su semana. Declararlo seria una lista mas que
    mantener, y la primera vez que alguien se olvidara de actualizarla el
    informe diria un numero que no es.
    """
    import subprocess
    de_commit = {COMMITS[corto]: semana
                 for corto, semana in SEMANA_DE_COMMIT.items()}
    cuenta = {}
    vistos = set()
    for _, info in sorted(TARJETAS.items()):
        for archivo, cuantas, _ in info["pruebas"]:
            if archivo in vistos:
                continue
            vistos.add(archivo)
            r = subprocess.run(["git", "log", "--diff-filter=A", "--format=%H",
                                "--", archivo],
                               capture_output=True, text=True, cwd=CODIGO)
            sha = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else None
            semana = de_commit.get(sha)
            if semana:
                cuenta[semana] = cuenta.get(semana, 0) + cuantas
    return cuenta


def semana(d, numero: int, contadores: dict) -> None:
    info = SEMANAS[numero]
    d.add_paragraph("%d. %s" % (numero + 2, info["titulo"]), style="Heading 1")

    # --- lo que pedia el plan, con la captura
    d.add_paragraph("%d.1 Lo que pedía el plan de trabajo" % (numero + 2),
                    style="Heading 2")
    parrafo(d, "El plan de trabajo compromete para esta semana lo siguiente. La "
               "figura reproduce la página tal como está en el documento "
               "presentado, sin reescribirla.")
    contadores["figura"] += 1
    figura(d, "plan-semana-%d.png" % numero,
           "Figura %d.%d. Semana %d del plan de trabajo. Fuente: "
           "planificacion_de_proyecto.pdf, página %d."
           % (numero + 2, contadores["figura"], numero, info["pagina"]),
           alto_maximo_mm=118)

    parrafo(d, "", despues=4)
    p = parrafo(d, "")
    p.add_run("Entregable comprometido: ").bold = True
    p.add_run(info["entregable"])
    if info.get("reunion"):
        p = parrafo(d, "")
        p.add_run("En la reunión se muestra: ").bold = True
        p.add_run(info["reunion"])
    p = parrafo(d, "")
    p.add_run("Punto de negocio de la semana: ").bold = True
    p.add_run(info["negocio"])
    parrafo(d, "El punto de negocio no forma parte de este informe, que cubre "
               "únicamente la construcción del sistema.", tamano=10, cursiva=True)

    # --- cada tarea
    tarjetas = [(n, t) for n, t in sorted(TARJETAS.items()) if t["semana"] == numero]
    for i, (n, ficha) in enumerate(tarjetas, start=2):
        tarea(d, numero, i, n, ficha, contadores)
    salto(d)


def tarea(d, num_semana: int, orden: int, numero: int, ficha: dict,
          contadores: dict) -> None:
    capitulo = num_semana + 2
    d.add_paragraph("%d.%d %s" % (capitulo, orden, ficha["titulo"]),
                    style="Heading 2")

    p = parrafo(d, "")
    p.add_run("En el plan: ").bold = True
    p.add_run("«%s»" % ficha["plan"]).italic = True

    p = parrafo(d, "")
    p.add_run("Tarjeta del tablero: ").bold = True
    enlace(p, "#%d — %s" % (numero, ficha["titulo"]),
           "https://github.com/%s/issues/%d" % (REPO, numero))

    # --- paso a paso
    d.add_paragraph("Qué se hizo", style="Heading 3")
    for i, paso in enumerate(ficha["pasos"], 1):
        pp = d.add_paragraph()
        pp.paragraph_format.left_indent = Mm(8)
        pp.paragraph_format.space_after = Pt(4)
        marca = pp.add_run("%d.  " % i)
        marca.bold = True
        pp.add_run(_sin_marcas(paso))

    # --- archivos
    d.add_paragraph("Archivos que quedaron escritos", style="Heading 3")
    filas = []
    for archivo, corto, que in ficha["archivos"]:
        url = "https://github.com/%s/blob/%s/%s" % (REPO, COMMITS[corto], archivo)
        filas.append([(archivo, url), que, corto])
    contadores["tabla"] += 1
    tabla_de(d, ["Archivo", "Qué resuelve", "Commit"], filas,
             anchos_mm=[64, 73, 22],
             epigrafe="Tabla %d.%d. Archivos de la tarea %s. Cada nombre enlaza "
                      "al archivo en el commit indicado. Fuente: elaboración "
                      "propia." % (capitulo, contadores["tabla"],
                                   ficha["titulo"].split(" ·")[0]))

    # --- pruebas
    if ficha["pruebas"]:
        d.add_paragraph("Pruebas", style="Heading 3")
        filas = []
        ultimo = COMMITS["c099013"]
        for archivo, cuantas, que in ficha["pruebas"]:
            url = "https://github.com/%s/blob/%s/%s" % (REPO, ultimo, archivo)
            filas.append([(archivo, url), str(cuantas), _sin_marcas(que)])
        contadores["tabla"] += 1
        tabla_de(d, ["Archivo de pruebas", "Cuántas", "Qué cubren"], filas,
                 anchos_mm=[52, 19, 88],
                 epigrafe="Tabla %d.%d. Pruebas de la tarea %s. Fuente: "
                          "elaboración propia."
                          % (capitulo, contadores["tabla"],
                             ficha["titulo"].split(" ·")[0]))

    # --- commits
    d.add_paragraph("Commits", style="Heading 3")
    for corto in ficha["commits"]:
        p = parrafo(d, "", despues=2)
        p.paragraph_format.left_indent = Mm(8)
        enlace(p, corto, "https://github.com/%s/commit/%s" % (REPO, COMMITS[corto]))
        p.add_run("   " + _mensaje(corto)).font.size = Pt(10)

    # --- codigo
    for archivo in CODIGO_DESTACADO.get(numero, []):
        nombre = _nombre_figura(archivo)
        if not os.path.exists(os.path.join(IMAGENES, nombre)):
            continue
        contadores["figura"] += 1
        figura(d, nombre,
               "Figura %d.%d. %s. Fuente: elaboración propia."
               % (capitulo, contadores["figura"], archivo),
               alto_maximo_mm=112)
        parrafo(d, "", despues=2)

    # --- pantallas
    for imagen, epigrafe in PANTALLAS.get(numero, []):
        contadores["figura"] += 1
        figura(d, imagen,
               "Figura %d.%d. %s Fuente: elaboración propia."
               % (capitulo, contadores["figura"], epigrafe),
               alto_maximo_mm=118)
        parrafo(d, "", despues=2)

    # --- notas y hallazgos
    if ficha.get("notas"):
        d.add_paragraph("Para tener en cuenta", style="Heading 3")
        for nota in ficha["notas"]:
            vineta(d, _sin_marcas(nota))

    if ficha.get("hallazgos"):
        d.add_paragraph("Deuda técnica detectada", style="Heading 3")
        for h in ficha["hallazgos"]:
            pp = vineta(d, "")
            enlace(pp, "Tarjeta #%d del tablero" % h,
                   "https://github.com/%s/issues/%d" % (REPO, h))


def _mensaje(corto: str) -> str:
    """El asunto del commit, leido del repositorio."""
    import subprocess
    r = subprocess.run(["git", "log", "-1", "--format=%s", COMMITS[corto]],
                       capture_output=True, text=True, cwd=CODIGO)
    return r.stdout.strip()


def _sin_marcas(texto: str) -> str:
    """Saca el resaltado de markdown, que en Word no significa nada."""
    return texto.replace("**", "").replace("`", "")


def deuda(d) -> None:
    d.add_paragraph("9. Deuda técnica detectada durante la construcción",
                    style="Heading 1")
    parrafo(d, "Construir el sistema contra la especificación dejó al "
               "descubierto quince diferencias entre el documento de análisis, "
               "los diagramas y lo que el sistema necesita para funcionar. "
               "Ninguna se resolvió por las malas: cada una quedó registrada con "
               "qué dice cada fuente, por qué es un problema y qué hay que hacer.")
    parrafo(d, "El detalle completo está en el archivo "
               "modelo-ea/CORRECCIONES-PENDIENTES.md del repositorio de "
               "documentación, y cada hallazgo tiene además su tarjeta en el "
               "tablero. Se separan en dos grupos, porque se corrigen en lugares "
               "distintos.")

    d.add_paragraph("9.1 Correcciones sobre el modelo de Enterprise Architect",
                    style="Heading 2")
    parrafo(d, "Son diferencias entre los diagramas y el modelo de datos. Se "
               "corrigen sobre el archivo shopMetrics.eapx, que sólo abre en la "
               "máquina con Windows, y después hay que volver a exportar los "
               "diagramas.")
    tabla_de(d,
             ["N.º", "Hallazgo"],
             [["1", "El doble factor no tiene dónde guardarse en el modelo de datos."],
              ["2", "Rol figura como enumeración en un diagrama y como tabla en el modelo."],
              ["3", "La asociación con los centros pierde su clase asociativa."],
              ["4", "La enumeración de operaciones dice SIN_ACCESO donde el caso de uso dice eliminación."],
              ["5", "Falta el campo descripcion en la entidad rol del diccionario."],
              ["6", "El atributo del permiso se llama categoria en el diagrama y recurso en el modelo."],
              ["7", "Verificar que la notificación de cambio de permisos esté en el diagrama de secuencia."],
              ["10", "Las multiplicidades hacia Alerta deben pasar de 1 a 0..1 en tres asociaciones."]],
             anchos_mm=[12, 147],
             epigrafe="Tabla 9.1. Correcciones pendientes sobre el modelo de "
                      "Enterprise Architect. Fuente: elaboración propia.")

    parrafo(d, "", despues=6)
    d.add_paragraph("9.2 Huecos del documento de análisis", style="Heading 2")
    parrafo(d, "Éstos no son diferencias entre el diagrama y el modelo: son "
               "cosas que el documento no dice o que dice de dos maneras "
               "distintas. La corrección va sobre el informe, no sobre los "
               "diagramas.")
    tabla_de(d,
             ["N.º", "Hallazgo", "Cómo se resolvió mientras tanto"],
             [["8", "Un local vacante no se puede representar, y la vacancia es "
                    "uno de los cuatro indicadores del tablero.",
               "El indicador se calcula y viaja marcado como dato parcial."],
              ["9", "El paso 5 del CU-001-001 pide una latencia promedio y a la "
                    "vez dice que no se almacena.",
               "Se muestra la latencia del sondeo del momento."],
              ["11", "El estado de la alerta se llama distinto en el "
                     "diccionario, en el CU-007-001 y en el CU-026-001.",
               "El código usa los valores del diccionario."],
              ["12", "alerta.zona_id es obligatorio, pero una regla sobre un "
                     "indicador del centro no es de ninguna zona.",
               "La alerta se cuelga de la primera zona del centro."]],
             anchos_mm=[12, 84, 63],
             epigrafe="Tabla 9.2. Huecos del documento de análisis detectados al "
                      "construir. Fuente: elaboración propia.")

    parrafo(d, "", despues=6)
    d.add_paragraph("9.3 Una corrección que hubo que hacer sobre la marcha",
                    style="Heading 2")
    parrafo(d, "El hallazgo 10 es el único que no se pudo dejar anotado para "
               "después, porque bloqueaba la construcción de la semana 6. El "
               "diccionario definía tres claves foráneas de la entidad alerta "
               "como obligatorias, aunque sus propias descripciones decían lo "
               "contrario: «si aplica» para la regla que la originó, «cuando la "
               "alerta es de negocio» para el locatario. Ninguna de las dos "
               "usaba la palabra que el generador del esquema reconoce para "
               "emitir una columna que admita nulos.")
    parrafo(d, "Con las tres columnas obligatorias no se podía guardar ninguna "
               "alerta: una recién generada no tiene responsable asignado —el "
               "paso 7 del CU-026-001 es justamente donde se lo asigna— y una "
               "generada por el modelo no nace de ninguna regla de umbral. Se "
               "corrigieron las descripciones del diccionario sin cambiar lo que "
               "significaban, se regeneró el esquema y se agregó una migración "
               "para las bases ya creadas.")
    salto(d)


def cierre(d) -> None:
    d.add_paragraph("10. Estado al cierre de la semana 6", style="Heading 1")

    tabla_de(d, ["", "Estado"],
             [["Tareas del plan cerradas", "19 de 19, con evidencia en cada tarjeta"],
              ["Casos de uso con endpoints", "10 de los 31 especificados"],
              ["Pruebas de la API", "191, todas en verde"],
              ["Pruebas del panel", "76, todas en verde"],
              ["Nivelación con el documento", "En verde"],
              ["Entidades en la base", "30 tablas, 43 claves foráneas"],
              ["Hipertablas de TimescaleDB", "2, con 2 agregados continuos"],
              ["Migraciones aplicadas", "4, reproducibles desde cero"],
              ["Deuda técnica registrada", "15 hallazgos, todos con tarjeta"]],
             anchos_mm=[62, 97],
             epigrafe="Tabla 10.1. Estado del sistema al cierre de la semana 6. "
                      "Fuente: elaboración propia.")

    parrafo(d, "", despues=8)
    d.add_paragraph("10.1 Lo que sigue", style="Heading 2")
    parrafo(d, "Las semanas 7 a 11 del plan continúan con la detección de "
               "anomalías y el score de vacancia, el portal del locatario, la "
               "vista de operaciones para celular, la auditoría y el despliegue, "
               "y la especificación de los casos de prueba. Las tarjetas ya están "
               "creadas en el tablero con el mismo nivel de detalle que las de "
               "estas seis semanas.")

    d.add_paragraph("10.2 Repositorios", style="Heading 2")
    for nombre, url, que in (
            ("shopmetrics", "https://github.com/javieravellanedaa/shopmetrics",
             "el sistema, el panel, los simuladores y el generador"),
            ("ShopMetrics-TFI", "https://github.com/javieravellanedaa/ShopMetrics-TFI",
             "la documentación, los diagramas y este informe")):
        p = parrafo(d, "", despues=3)
        p.paragraph_format.left_indent = Mm(8)
        enlace(p, nombre, url)
        p.add_run("   " + que)



USUARIOS = [
    ("admin@shopmetrics.com.ar", "Javier Gómez", "Administrador del centro",
     "Ve y hace todo: las cinco secciones del menú, las acciones correctivas "
     "sobre las integraciones, crear y pausar reglas, atender alertas."),
    ("gerente@shopmetrics.com.ar", "Marina Acuña", "Gerente",
     "Ve las cinco secciones y puede exportar, pero no escribe: cualquier "
     "acción correctiva o cambio de configuración se rechaza."),
    ("operaciones@shopmetrics.com.ar", "Ana Pérez", "Operaciones",
     "Entra a «Mi turno». El menú se recorta: sin Reglas de alerta ni "
     "Integraciones, porque su rol no opera sobre configuración."),
    ("locatario@shopmetrics.com.ar", "Indumentaria K", "Locatario",
     "Entra a «Mi local». Sólo lectura. Su portal propio se construye en la "
     "semana 8."),
]

CLAVE = "Shop2026x"


def guia(d) -> None:
    """El manual de uso: como se instala, como se entra y que hace cada rol.

    Los pasos no se reescriben: son los mismos del guion del recorrido, que ya
    esta redactado en segunda persona y cubre los cuatro roles y todos los
    controles de cada pantalla. Tener una sola fuente evita que el video y el
    informe digan cosas distintas.
    """
    contadores = {"figura": 0, "tabla": 0}

    d.add_paragraph("11. Guía de uso", style="Heading 1")
    parrafo(d, "Este capítulo es para quien tiene que poner el sistema a andar "
               "sin haberlo construido. Primero qué hace falta y con qué "
               "comandos se levanta, después con qué usuario se entra, y al "
               "final el recorrido completo: los ocho casos de uso que hoy "
               "funcionan, con los cuatro roles y todos los botones de cada "
               "pantalla, incluidos los que rechazan.")

    # ------------------------------------------------------------ instalacion
    d.add_paragraph("11.1 Qué hace falta", style="Heading 2")
    parrafo(d, "Tres programas, y nada más. El sistema no necesita que se "
               "instale ninguna base de datos a mano: la levanta él mismo "
               "dentro de un contenedor.")
    contadores["tabla"] += 1
    tabla_de(d,
             ["Programa", "Versión", "Para qué"],
             [["Docker", "cualquiera reciente",
               "Corre la base de datos PostgreSQL con TimescaleDB y los dos "
               "simuladores de los sistemas externos."],
              ["Python", "3.11 o más nuevo",
               "La API y las herramientas de línea de comandos."],
              ["Node.js", "20 o más nuevo",
               "El panel web."]],
             anchos_mm=[26, 36, 97],
             epigrafe="Tabla 11.%d. Lo que hay que tener instalado antes de "
                      "empezar. Fuente: elaboración propia."
                      % contadores["tabla"])

    parrafo(d, "", despues=6)
    parrafo(d, "No hace falta verificarlos de antemano: el primer comando los "
               "controla y, si falta alguno, dice cuál y cómo conseguirlo en "
               "lugar de fallar a la mitad.")

    # ------------------------------------------------------------- los pasos
    parrafo(d, "", despues=6)
    d.add_paragraph("11.2 Instalación en una máquina nueva", style="Heading 2")
    parrafo(d, "Dos comandos, una sola vez:")
    for orden, comando, que in (
            ("1", "git clone https://github.com/javieravellanedaa/shopmetrics",
             "Trae el código."),
            ("2", "cd shopmetrics && make instalar",
             "Comprueba los tres programas, instala las dependencias de la API "
             "y del panel, crea la base, aplica las cuatro migraciones y da de "
             "alta los usuarios de los cuatro roles.")):
        p = parrafo(d, "", despues=2)
        p.paragraph_format.left_indent = Mm(8)
        p.add_run(orden + ".  ").bold = True
        c = p.add_run(comando)
        c.font.name = "Courier New"
        c.font.size = Pt(10)
        p = parrafo(d, que, despues=6)
        p.paragraph_format.left_indent = Mm(14)

    parrafo(d, "La instalación tarda unos minutos, casi todos en bajar las "
               "dependencias. Termina informando cuántas tablas quedaron "
               "creadas; si dice 30, está completa.")

    contadores["figura"] += 1
    figura(d, "guia-instalar.png",
           "Figura 11.%d. Salida de make instalar sobre una máquina sin nada "
           "instalado. Fuente: elaboración propia."
           % contadores["figura"], alto_maximo_mm=70)

    # ------------------------------------------------------------- arrancar
    parrafo(d, "", despues=6)
    d.add_paragraph("11.3 Cómo se pone en marcha", style="Heading 2")
    parrafo(d, "Una vez instalado, todo se maneja con cuatro comandos. Se "
               "corren parados en la carpeta del proyecto.")
    contadores["tabla"] += 1
    tabla_de(d,
             ["Comando", "Qué hace"],
             [["make instalar",
               "Deja la máquina lista. Sólo la primera vez."],
              ["make arrancar",
               "Levanta la base, los dos simuladores, la API y el panel. "
               "Espera a que cada uno responda y termina mostrando las "
               "direcciones y los usuarios."],
              ["make demostracion",
               "Lo mismo, y además arma el centro —zonas, locatarios, "
               "conectores y sensores— y genera datos, para que el panel abra "
               "con números en lugar de vacío. Es el que conviene para "
               "mostrarlo."],
              ["make parar",
               "Apaga todo."]],
             anchos_mm=[38, 121],
             epigrafe="Tabla 11.%d. Los cuatro comandos que manejan el "
                      "sistema. Fuente: elaboración propia."
                      % contadores["tabla"])

    parrafo(d, "", despues=6)
    parrafo(d, "Escribir make a secas lista todos los comandos disponibles con "
               "su descripción.")

    contadores["figura"] += 1
    figura(d, "guia-demostracion.png",
           "Figura 11.%d. Final de make demostracion: el centro armado, los "
           "datos generados y las direcciones donde queda escuchando cada "
           "parte. Fuente: elaboración propia." % contadores["figura"],
           alto_maximo_mm=95)

    # ---------------------------------------------------------- direcciones
    parrafo(d, "", despues=6)
    d.add_paragraph("11.4 Dónde queda cada cosa", style="Heading 2")
    contadores["tabla"] += 1
    tabla_de(d,
             ["Qué", "Dirección", "Para qué"],
             [["Panel", "http://localhost:3000",
               "La aplicación. Es por donde se entra."],
              ["API", "http://localhost:8000/docs",
               "La documentación de los endpoints, generada sola, donde se "
               "los puede probar uno por uno."],
              ["Base de datos", "http://localhost:8080",
               "Adminer: permite mirar las 30 tablas y lo que hay cargado."],
              ["Simulador de puntos de venta", "http://localhost:9001/docs",
               "El sistema externo que emula las cinco cajas. Desde acá se lo "
               "puede hacer fallar a propósito."],
              ["Simulador de sensores", "http://localhost:9002/docs",
               "El que emula los tres sensores de conteo."]],
             anchos_mm=[44, 48, 67],
             epigrafe="Tabla 11.%d. Direcciones del sistema levantado. Fuente: "
                      "elaboración propia." % contadores["tabla"])

    parrafo(d, "", despues=6)
    parrafo(d, "Las direcciones son locales: el sistema escucha únicamente en "
               "la máquina donde se lo levantó. Publicarlo en un servidor es "
               "parte de la semana 10 del plan.", tamano=10, cursiva=True)

    # ------------------------------------------------------------- usuarios
    parrafo(d, "", despues=6)
    d.add_paragraph("11.5 Con qué usuario se entra", style="Heading 2")
    parrafo(d, "La instalación da de alta un usuario por cada uno de los "
               "cuatro roles. Los cuatro tienen la misma clave: ")
    p = parrafo(d, "", despues=6)
    p.paragraph_format.left_indent = Mm(8)
    c = p.add_run(CLAVE)
    c.bold = True
    c.font.name = "Courier New"
    c.font.size = Pt(12)

    contadores["tabla"] += 1
    tabla_de(d,
             ["Correo", "Rol", "Qué puede hacer"],
             [[correo, "%s\n%s" % (rol, nombre), que]
              for correo, nombre, rol, que in USUARIOS],
             anchos_mm=[62, 28, 69],
             epigrafe="Tabla 11.%d. Usuarios creados por la instalación. La "
                      "clave de los cuatro es %s. Fuente: elaboración propia."
                      % (contadores["tabla"], CLAVE))

    parrafo(d, "", despues=6)
    parrafo(d, "Las claves están a la vista a propósito. Estos cuatro usuarios "
               "existen sólo dentro de una base que se recrea desde cero en "
               "cada instalación y que no contiene ningún dato real; fuera de "
               "ella no sirven para nada. En un entorno de verdad los usuarios "
               "se cargan desde variables de entorno, que nunca se versionan.")
    parrafo(d, "Conviene entrar con los cuatro. Es la forma de ver que la "
               "matriz de permisos se aplica de verdad: el menú cambia según "
               "el rol, y lo que el menú esconde el backend igual lo rechaza "
               "si se fuerza la dirección a mano.")

    salto(d)

    # ------------------------------------------------------------- recorrido
    d.add_paragraph("11.6 El recorrido, paso a paso", style="Heading 2")
    parrafo(d, "Los %d pasos que siguen recorren los ocho casos de uso que hoy "
               "funcionan, pasando por los cuatro roles y por todos los "
               "controles de cada pantalla, incluidos los que rechazan: el "
               "ingreso con credenciales que no sirven, el gerente que no "
               "puede escribir, la acción correctiva que no resuelve, la "
               "validación que frena un umbral imposible."
               % len(PASOS))
    parrafo(d, "Es el mismo recorrido del video ShopMetrics-recorrido.mp4 que "
               "acompaña a este informe. Cada paso lleva la captura de lo que "
               "se ve en la pantalla en ese momento.")

    caso_actual = None
    for orden, (archivo, caso, titulo, detalle, nota) in enumerate(PASOS, start=1):
        if caso != caso_actual:
            caso_actual = caso
            info = CASOS[caso]
            parrafo(d, "", despues=4)
            d.add_paragraph("%s · %s" % (caso, info["nombre"]),
                            style="Heading 3")
            parrafo(d, info["resumen"], cursiva=True, despues=6)

        p = parrafo(d, "", antes=6, despues=2)
        p.add_run("Paso %d. " % orden).bold = True
        p.add_run(titulo).bold = True

        p = parrafo(d, detalle, despues=2)
        p.paragraph_format.left_indent = Mm(6)

        if nota:
            p = parrafo(d, nota, tamano=10, cursiva=True, despues=4)
            p.paragraph_format.left_indent = Mm(6)

        contadores["figura"] += 1
        figura(d, "%s.jpg" % archivo,
               "Figura 11.%d. Paso %d: %s Fuente: elaboración propia."
               % (contadores["figura"], orden,
                  titulo[0].lower() + titulo[1:] + "."),
               carpeta=CAPTURAS, alto_maximo_mm=68)


def limpiar_medios(ruta: str) -> int:
    """Saca del .docx las imagenes que ya no usa nadie.

    El documento se arma sobre el Word del trabajo final, que trae casi veinte
    megas de figuras. Al vaciar el cuerpo esas imagenes dejan de mostrarse, pero
    siguen adentro del paquete porque **sacar un parrafo no saca su relacion**:
    el archivo pesa lo mismo y arrastra material de otra entrega.

    Hay que ir por los dos lados: primero sacar de `document.xml.rels` las
    relaciones de imagen que ningun `r:embed` del cuerpo nombra, y recien
    despues borrar los archivos que quedaron sin nadie que los apunte. Se
    conservan las del encabezado y el pie, que traen el escudo de la
    Universidad.
    """
    import re
    import zipfile

    with zipfile.ZipFile(ruta) as paquete:
        contenido = {n: paquete.read(n) for n in paquete.namelist()}

    cuerpo = contenido["word/document.xml"].decode("utf-8", "ignore")
    en_uso = set(re.findall(r'r:(?:embed|id|link)="([^"]+)"', cuerpo))

    rels = contenido["word/_rels/document.xml.rels"].decode("utf-8", "ignore")
    sacadas = []

    def decidir(coincidencia):
        entrada = coincidencia.group(0)
        ident = re.search(r'Id="([^"]+)"', entrada)
        destino = re.search(r'Target="([^"]+)"', entrada)
        if (ident and destino and "media/" in destino.group(1)
                and ident.group(1) not in en_uso):
            sacadas.append(destino.group(1))
            return ""
        return entrada

    rels = re.sub(r"<Relationship\b[^>]*/>", decidir, rels)
    contenido["word/_rels/document.xml.rels"] = rels.encode("utf-8")

    # Que medios quedan nombrados por alguna relacion, del cuerpo o de otra parte.
    vivos = set()
    for interno, datos in contenido.items():
        if interno.endswith(".rels"):
            for destino in re.findall(r'Target="([^"]+)"',
                                      datos.decode("utf-8", "ignore")):
                if "media/" in destino:
                    vivos.add("word/" + destino.lstrip("./"))

    huerfanos = [n for n in contenido
                 if n.startswith("word/media/") and n not in vivos]
    for n in huerfanos:
        del contenido[n]

    temporal = ruta + ".tmp"
    with zipfile.ZipFile(temporal, "w", zipfile.ZIP_DEFLATED) as nuevo:
        for interno, datos in contenido.items():
            nuevo.writestr(interno, datos)
    shutil.move(temporal, ruta)
    return len(huerfanos)


def main() -> int:
    if not os.path.exists(PLANTILLA):
        print("No encuentro la plantilla en %s" % PLANTILLA)
        return 1

    shutil.copy(PLANTILLA, SALIDA)
    d = docx.Document(SALIDA)
    vaciar(d)

    poner_al_dia_encabezado(d)

    contadores = {"figura": 0, "tabla": 0}
    portada(d)
    introduccion(d)
    resumen(d)
    for numero in sorted(SEMANAS):
        contadores["figura"] = 0
        contadores["tabla"] = 0
        semana(d, numero, contadores)
    deuda(d)
    cierre(d)
    salto(d)
    guia(d)

    d.save(SALIDA)
    antes = os.path.getsize(SALIDA)
    sacadas = limpiar_medios(SALIDA)
    print("escrito: %s (%.1f MB)" % (SALIDA, os.path.getsize(SALIDA) / 1e6))
    print("  se sacaron %d imágenes de la plantilla (%.1f MB menos)"
          % (sacadas, (antes - os.path.getsize(SALIDA)) / 1e6))
    return 0


if __name__ == "__main__":
    sys.exit(main())
