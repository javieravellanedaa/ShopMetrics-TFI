# -*- coding: utf-8 -*-
"""Actualiza 10.5.8: DER nuevo + 8 diagramas por area + diccionario de datos al dia."""
import sys, io, os, copy, shutil, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH as AL
from PIL import Image

D   = r"D:\Javier\UAI\UAI - SAP\STF\STF\Primera entrega\STF_Gomez_Javier_E1_v1.docx"
BK  = r"D:\Javier\UAI\UAI - SAP\STF\STF\Primera entrega\Backups\STF_Gomez_Javier_E1_v1.BACKUP-preDER.docx"
EA  = r"D:\Javier\UAI\UAI - SAP\shopMetrics\shopMetrics\enterprise_architect"
SUB = os.path.join(EA, "export", "der")
if not os.path.exists(BK):
    shutil.copy2(D, BK)

doc = Document(D)
W  = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
def blocks(parent):
    for ch in parent.element.body.iterchildren():
        if ch.tag == W+"p":  yield Paragraph(ch, parent)
        elif ch.tag == W+"tbl": yield Table(ch, parent)
seq = list(blocks(doc))
ini = [i for i,b in enumerate(seq) if isinstance(b,Paragraph) and b.text.strip().startswith("10.5.8")][-1]

# ---------------------------------------------------------------- indice entidad -> tabla
tablas = {}
for i in range(ini, len(seq)):
    b = seq[i]
    if isinstance(b, Paragraph):
        m = re.match(r'^([a-z_]+):\s', b.text.strip())
        if m and i+1 < len(seq) and isinstance(seq[i+1], Table):
            tablas[m.group(1)] = (b, seq[i+1], i+1)
print("entidades con tabla en el diccionario:", len(tablas))

def fila(tab, campo, tipo, clave, desc):
    """agrega una fila copiando el formato de la ultima"""
    ult = tab.rows[-1]._tr
    nueva = copy.deepcopy(ult)
    ult.addnext(nueva)
    tab._tbl.remove(nueva); ult.addnext(nueva)
    r = tab.rows[-1]
    for celda, txt in zip(r.cells, [campo, tipo, clave, desc]):
        p = celda.paragraphs[0]
        for extra in celda.paragraphs[1:]:
            extra._p.getparent().remove(extra._p)
        if p.runs:
            p.runs[0].text = txt
            for rr in p.runs[1:]:
                rr._r.getparent().remove(rr._r)
        else:
            p.add_run(txt)

# ---------------------------------------------------------------- 1) campos nuevos
NUEVOS = {
 "alerta": [("modelo_id","UUID","FK","Modelo de ML que generó la alerta. Nulo si proviene de una regla de umbral."),
            ("locatario_id","UUID","FK","Locatario afectado, cuando la alerta es de negocio y no de zona."),
            ("asignado_a","UUID","FK","Usuario responsable de atender la alerta.")],
 "local": [("zona_id","UUID","FK","Zona del centro donde se ubica el local.")],
 "regla_alerta": [("centro_id","UUID","FK","Centro al que pertenece la regla.")],
 "evento_auditoria": [("centro_id","UUID","FK","Centro sobre el que se ejecutó la acción.")],
 "reporte": [("centro_id","UUID","FK","Centro sobre el que se generó el reporte.")],
}
for ent, campos in NUEVOS.items():
    _, tab, _ = tablas[ent]
    ya = {r.cells[0].text.strip() for r in tab.rows}
    for c in campos:
        if c[0] in ya: continue
        fila(tab, *c)
        print(f"  + {ent}.{c[0]}")

# centro_acceso: rol VARCHAR -> rol_id UUID PK,FK
_, tab, _ = tablas["centro_acceso"]
for r in tab.rows:
    if r.cells[0].text.strip() == "rol":
        for celda, txt in zip(r.cells, ["rol_id","UUID","PK, FK","Rol del usuario dentro de ese centro."]):
            p = celda.paragraphs[0]
            if p.runs:
                p.runs[0].text = txt
                for rr in p.runs[1:]: rr._r.getparent().remove(rr._r)
            else: p.add_run(txt)
        print("  ~ centro_acceso.rol -> rol_id (FK a rol)")

# ---------------------------------------------------------------- 2) entidades nuevas
ENT_NUEVAS = [
 ("regla_destinatario", "Destinatarios de una regla de alerta y canal por el que se les notifica.",
  [("regla_id","UUID","PK, FK","Regla de alerta."),
   ("usuario_id","UUID","PK, FK","Usuario destinatario."),
   ("canal","VARCHAR","","Canal de envío (push, email, WhatsApp).")]),
 ("resolucion_alerta", "Resolución en terreno de una alerta, con su causa, la acción tomada y el operario que la cerró.",
  [("id","UUID","PK","Identificador único de la resolución."),
   ("alerta_id","UUID","FK","Alerta resuelta."),
   ("usuario_id","UUID","FK","Operario que la resolvió."),
   ("causa","VARCHAR","","Causa identificada (máx. 500 caracteres)."),
   ("accion_tomada","VARCHAR","","Acción tomada (resolver, escalar, derivar)."),
   ("checklist_resumen","VARCHAR","","Resumen del resultado del checklist ejecutado."),
   ("fecha_resolucion","TIMESTAMP","","Fecha y hora de cierre de la alerta.")]),
 ("recomendacion", "Recomendación generada por un modelo de optimización, de mix del centro o de acción para un local.",
  [("id","UUID","PK","Identificador único de la recomendación."),
   ("modelo_id","UUID","FK","Modelo de ML que la generó."),
   ("centro_id","UUID","FK","Centro sobre el que aplica."),
   ("locatario_id","UUID","FK","Locatario destinatario. Nulo si la recomendación es de mix del centro."),
   ("tipo","VARCHAR","","Tipo (sumar rubro, reducir rubro, reubicar, acción de local)."),
   ("rubro_objetivo","VARCHAR","","Rubro sobre el que recae la recomendación."),
   ("impacto_estimado","DECIMAL","","Impacto estimado en facturación."),
   ("confianza","DECIMAL","","Nivel de confianza del modelo (0.0 a 1.0)."),
   ("prioridad","VARCHAR","","Prioridad (alta, media, baja)."),
   ("fecha","TIMESTAMP","","Fecha y hora de generación.")]),
 ("recomendacion_decision", "Decisión del usuario sobre una recomendación; realimenta el modelo.",
  [("id","UUID","PK","Identificador único de la decisión."),
   ("recomendacion_id","UUID","FK","Recomendación evaluada."),
   ("usuario_id","UUID","FK","Usuario que decide."),
   ("decision","VARCHAR","","Decisión (adoptada, descartada)."),
   ("fecha","TIMESTAMP","","Fecha y hora de la decisión.")]),
 ("parametro_sistema", "Parámetro general de configuración del sistema, por centro.",
  [("id","UUID","PK","Identificador único del parámetro."),
   ("centro_id","UUID","FK","Centro al que aplica el parámetro."),
   ("usuario_id","UUID","FK","Usuario que realizó la última modificación."),
   ("clave","VARCHAR","","Nombre del parámetro."),
   ("valor","VARCHAR","","Valor configurado."),
   ("tipo_dato","VARCHAR","","Tipo de dato del valor."),
   ("fecha_modificacion","TIMESTAMP","","Fecha y hora del último cambio.")]),
]

# la ultima entidad del diccionario marca donde insertar
ult_par, ult_tab, _ = tablas["preferencia_notificacion"]
ancla = ult_tab._tbl
for nom, desc, campos in ENT_NUEVAS:
    if nom in tablas:
        print(f"  = {nom} ya estaba"); continue
    # parrafo descriptor, copiando formato del de preferencia_notificacion
    np = copy.deepcopy(ult_par._p)
    ancla.addnext(np); ancla = np
    pp = Paragraph(np, ult_par._parent)
    if pp.runs:
        pp.runs[0].text = f"{nom}: {desc}"
        for rr in pp.runs[1:]: rr._r.getparent().remove(rr._r)
    # tabla: copiar la de preferencia_notificacion y dejar solo el encabezado
    nt = copy.deepcopy(ult_tab._tbl)
    ancla.addnext(nt); ancla = nt
    t = Table(nt, ult_tab._parent)
    for r in list(t.rows[1:]):
        nt.remove(r._tr)
    for c in campos:
        fila(t, *c)
    print(f"  + entidad {nom} ({len(campos)} campos)")

doc.save(D)
print("diccionario actualizado")
