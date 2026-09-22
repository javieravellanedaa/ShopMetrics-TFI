# -*- coding: utf-8 -*-
"""Inserta el anexo de capacidad operativa en el punto 8 del informe,
renumera las figuras posteriores y agrega la explicacion del origen de los datos."""
import sys, io, re, copy, shutil, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH as AL

D   = r"D:\Javier\UAI\UAI - SAP\STF\STF\Primera entrega\STF_Gomez_Javier_E1_v1.docx"
BK  = r"D:\Javier\UAI\UAI - SAP\STF\STF\Primera entrega\Backups\STF_Gomez_Javier_E1_v1.BACKUP-preanexo.docx"
IMG = r"D:\Javier\UAI\UAI - SAP\STF\STF\Primera entrega\img_punto8"
if not os.path.exists(BK):
    shutil.copy2(D, BK)

doc = Document(D)
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

# ---------------------------------------------------------------- 1) renumerar 8.15..8.22 -> 8.31..8.38
MAPA = {15: 31, 16: 32, 17: 33, 18: 34, 19: 35, 20: 36, 21: 37, 22: 38}
cambios = 0
for p in doc.paragraphs:
    if "Figura 8." not in p.text:
        continue
    for r in p.runs:
        def sub(m):
            n = int(m.group(1))
            return f"Figura 8.{MAPA[n]}" if n in MAPA else m.group(0)
        nuevo = re.sub(r"Figura 8\.(\d+)", sub, r.text)
        if nuevo != r.text:
            r.text = nuevo
            cambios += 1
print("runs de caption renumerados:", cambios)

# ---------------------------------------------------------------- 2) helpers
def sectpr_de(idx):
    """Copia el sectPr del parrafo idx (define la seccion que termina ahi)."""
    pPr = doc.paragraphs[idx]._p.find(W + "pPr")
    return copy.deepcopy(pPr.find(W + "sectPr"))

SECT_PORTRAIT  = sectpr_de(570)
SECT_LANDSCAPE = sectpr_de(580)
assert SECT_PORTRAIT is not None and SECT_LANDSCAPE is not None

def poner_sectpr(par, sect):
    p = par._p
    pPr = p.find(W + "pPr")
    if pPr is None:
        pPr = p.makeelement(W + "pPr", {})
        p.insert(0, pPr)
    pPr.append(copy.deepcopy(sect))

def hacer(anchor_p, estilo="Normal"):
    p = doc.add_paragraph(style=estilo)
    anchor_p.addprevious(p._p)
    return p

def cuerpo(anchor, texto, negrita_hasta=None):
    p = hacer(anchor)
    p.alignment = AL.JUSTIFY
    if negrita_hasta:
        r = p.add_run(negrita_hasta); r.bold = True
        p.add_run(texto)
    else:
        p.add_run(texto)
    return p

def figura(anchor, archivo, ancho_cm, leyenda):
    pi = hacer(anchor)
    pi.alignment = AL.CENTER
    pi.paragraph_format.keep_with_next = True
    pi.paragraph_format.space_after = Pt(4)
    pi.add_run().add_picture(os.path.join(IMG, archivo), width=Cm(ancho_cm))
    pc = hacer(anchor)
    pc.alignment = AL.CENTER
    r = pc.add_run(leyenda); r.italic = True; r.font.size = Pt(9)
    return pi, pc

# ---------------------------------------------------------------- 3) origen de los datos (tras el intro del punto 8)
anc = doc.paragraphs[513]._p          # heading "8.1 Modelo de negocios: Canvas ajustado"
cuerpo(anc,
  "Todas las cifras que se presentan en este capítulo provienen de un único archivo de cálculo y están encadenadas por fórmula, "
  "de modo que ninguna se carga dos veces. La hoja Hipótesis fija los tres parámetros de partida: el tamaño del universo de "
  "comercios, el porcentaje de participación que se pretende alcanzar en cada ejercicio y la lista de precios de los seis "
  "servicios. De ahí se desprende la hoja Proy. ventas, que distribuye mes a mes las altas de cada plan y acumula los abonos "
  "vigentes, y que es la única hoja donde se cargan cantidades a mano.",
  "Origen de los datos. ")
cuerpo(anc,
  "El resto se calcula. El Anexo de capacidad operativa toma las cantidades de Proy. ventas y las convierte en horas hombre "
  "para determinar la dotación técnica necesaria. Las hojas Costos fijos, Costos variables y Costos RRHH toman de allí la "
  "dotación y de Proy. ventas las unidades, y devuelven la estructura de egresos. Los modelos de ingresos y de egresos "
  "consolidan esos resultados por ejercicio, y la matriz de riesgos valora las desviaciones posibles sobre ese mismo conjunto. "
  "Cada figura de este capítulo indica al pie la hoja de la que proviene, de manera que cualquier cifra pueda rastrearse hasta "
  "su origen.")

# ---------------------------------------------------------------- 4) subseccion 8.4.1
anc = doc.paragraphs[560]._p          # heading "8.5 Modelo de inversión"

h = hacer(anc, "Heading 3"); h.add_run("8.4.1 Anexo de capacidad operativa")

cuerpo(anc,
  "La estructura de recursos humanos no se define por criterio sino por volumen de trabajo. El anexo de capacidad operativa "
  "descompone cada servicio en las tareas que lo componen, asigna a cada tarea una base horaria y una cantidad requerida, y "
  "obtiene así las horas que consume una unidad vendida. Multiplicadas por las unidades de la proyección de ventas, esas bases "
  "horarias dan las horas hombre que la empresa necesita cubrir mes a mes; comparadas contra las horas que rinde un empleado, "
  "determinan cuántos técnicos hacen falta y en qué mes deben incorporarse.")
cuerpo(anc,
  "Un empleado dispone de 236 días laborales al año, resultado de descontar dos semanas de licencias y catorce días festivos "
  "sobre las cincuenta y dos semanas del calendario. Con jornada de ocho horas eso arroja 1.888 horas anuales teóricas, que se "
  "castigan a 1.800 anuales y 150 mensuales para contemplar la improductividad propia de cualquier puesto. Ese valor de 150 "
  "horas mensuales es el divisor de todo el anexo.",
  "Horas laborables por empleado. ")
cuerpo(anc,
  "El alta del Plan Básico consume media hora y es enteramente remota. La del Plan Vidriera consume tres horas e incluye el "
  "traslado, el montaje del sensor de vidriera y del contador de puerta, la conexión con el punto de venta y la prueba del "
  "embudo. La del Plan Cadena consume doce horas porque las tareas de montaje se repiten en los cinco locales. El soporte "
  "mensual consume 0,15, 0,25 y 0,60 horas por comercio activo según el plan, y se sostiene mientras el comercio permanece "
  "abonado.",
  "Consumo horario de cada servicio. ")
ultima_portrait = cuerpo(anc,
  "Valorizadas al costo horario del técnico, seis dólares la hora, las altas cuestan 3, 18 y 72 dólares de mano de obra contra "
  "precios de lista de 25, 60 y 250 dólares. Sumado el equipamiento que se instala en el local, el kit completo asciende a 3, 52 "
  "y 242 dólares respectivamente, de modo que el cargo de alta cubre el esfuerzo técnico y el material comprometido en los tres "
  "planes. El soporte mensual cuesta 0,90, 1,50 y 3,60 dólares por comercio, contra abonos de 15, 29 y 79 dólares.",
  "Costo del servicio. ")
poner_sectpr(ultima_portrait, SECT_PORTRAIT)

FIGS = [
 ("AN01_horas_laborables.png", 18.1, "Figura 8.15. Cálculo de las horas laborables de un empleado por mes. Fuente: planilla de presupuesto financiero, hoja Anexo capacidad operativa."),
 ("AN02_inst_basico.png",      24.9, "Figura 8.16. Desglose de tareas del alta e instalación del Plan Básico."),
 ("AN03_inst_vidriera.png",    24.9, "Figura 8.17. Desglose de tareas del alta e instalación del Plan Vidriera."),
 ("AN04_inst_cadena.png",      24.9, "Figura 8.18. Desglose de tareas del alta e instalación del Plan Cadena."),
 ("AN05_sop_basico.png",       24.1, "Figura 8.19. Desglose de tareas del soporte mensual del Plan Básico."),
 ("AN06_sop_vidriera.png",     24.1, "Figura 8.20. Desglose de tareas del soporte mensual del Plan Vidriera."),
 ("AN07_sop_cadena.png",       24.1, "Figura 8.21. Desglose de tareas del soporte mensual del Plan Cadena."),
 ("AN08_kit_basico.png",       11.8, "Figura 8.22. Costo del kit de instalación del Plan Básico."),
 ("AN09_kit_vidriera.png",     11.7, "Figura 8.23. Costo del kit de instalación del Plan Vidriera."),
 ("AN10_kit_cadena.png",       11.8, "Figura 8.24. Costo del kit de instalación del Plan Cadena."),
 ("AN11_hh_2026_s1.png",       24.9, "Figura 8.25. Horas hombre requeridas en 2026, primer semestre."),
 ("AN12_hh_2026_s2.png",       24.9, "Figura 8.26. Horas hombre requeridas en 2026, segundo semestre."),
 ("AN13_hh_2027_s1.png",       24.9, "Figura 8.27. Horas hombre requeridas en 2027, primer semestre."),
 ("AN14_hh_2027_s2.png",       24.9, "Figura 8.28. Horas hombre requeridas en 2027, segundo semestre."),
 ("AN15_hh_2028_s1.png",       24.9, "Figura 8.29. Horas hombre requeridas en 2028, primer semestre."),
 ("AN16_hh_2028_s2.png",       24.9, "Figura 8.30. Horas hombre requeridas en 2028, segundo semestre."),
]
ultima_caption = None
for arch, ancho, leg in FIGS:
    _, pc = figura(anc, arch, ancho, leg)
    ultima_caption = pc
poner_sectpr(ultima_caption, SECT_LANDSCAPE)

cuerpo(anc,
  "El total de horas hombre asciende a 440,75 en 2026, 1.113,75 en 2027 y 1.982,10 en 2028. Lo que define la dotación no es ese "
  "total sino el mes de mayor exigencia: 87,50 horas en diciembre de 2026, 123,35 en diciembre de 2027 y 189,65 en diciembre de "
  "2028. Contra las 150 horas mensuales de un empleado, un solo técnico cubre los dos primeros ejercicios; el segundo técnico se "
  "vuelve necesario en abril de 2028, que es el primer mes en que la carga supera ese umbral con 152,75 horas. Esa es la fecha "
  "que debe reflejar la estructura de costos de recursos humanos.",
  "Lectura del anexo. ")
cuerpo(anc,
  "El anexo dimensiona el área técnica, no el área comercial. La capacidad del vendedor y la productividad esperada por puesto "
  "comercial quedan pendientes de incorporación, del mismo modo que la conciliación entre la dotación que arroja este cálculo y "
  "la que finalmente se presupuesta en la hoja de costos de recursos humanos.",
  "Alcance. ")

doc.save(D)
print("guardado")

# ---------------------------------------------------------------- verificacion
d2 = Document(D)
print("secciones:", len(d2.sections), [str(s.orientation) for s in d2.sections])
for i, p in enumerate(d2.paragraphs):
    if re.search(r"Figura 8\.(1[5-9]|2\d|3[0-8])\.", p.text) or "8.4.1" in p.text:
        print(f"  [{i}] {p.text[:78]}")
