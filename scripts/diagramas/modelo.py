# -*- coding: utf-8 -*-
"""Modelo comun: diccionario, relaciones, dominios y nombres de clase."""
import json, re

ALIAS = {'centro':'centro_comercial','conector':'conector_pos','dispositivo':'dispositivo_iot',
         'regla':'regla_alerta','modelo':'modelo_ml','prediccion':'prediccion_vacancia',
         'asignado_a':'usuario','recomendacion':'recomendacion'}

DOMINIOS = [
 ("estructura","Estructura comercial","#1D5B8F","#E3EDF5",
  ["centro_comercial","zona","locatario","local"]),
 ("identidad","Identidad y permisos","#5C4489","#E9E4F2",
  ["usuario","rol","permiso","usuario_rol","rol_permiso","centro_acceso"]),
 ("ingesta","Ingesta de datos","#22685C","#DEEDEA",
  ["conector_pos","registro_pos","dispositivo_iot","evento_trafico"]),
 ("analitica","Indicadores, alertas y ML","#8F5310","#F6EADA",
  ["indicador","regla_alerta","regla_destinatario","modelo_ml","alerta",
   "resolucion_alerta","prediccion_vacancia","accion_retencion",
   "recomendacion","recomendacion_decision"]),
 ("gobierno","Gobierno y salida","#7E2F49","#F3E2E8",
  ["consentimiento","evento_auditoria","reporte","notificacion",
   "preferencia_notificacion","parametro_sistema"]),
]
DOM = {t:(d,col,claro) for d,_,col,claro,ts in DOMINIOS for t in ts}

OPCIONAL = re.compile(r'nulo|si aplica|opcional|cuando la', re.I)

# composiciones: la parte no existe sin el todo
COMPOSICION = {('centro_comercial','zona'), ('locatario','local'),
               ('conector_pos','registro_pos'), ('dispositivo_iot','evento_trafico'),
               ('alerta','resolucion_alerta'), ('prediccion_vacancia','accion_retencion'),
               ('recomendacion','recomendacion_decision'), ('regla_alerta','regla_destinatario')}

METODOS = {
 'centro_comercial':['+ agregarZona(z)','+ listarLocatarios()','+ ocupacion(): Decimal'],
 'zona':['+ agregarLocal(l)','+ traficoPorFranja(f)'],
 'locatario':['+ locales(): List','+ consentimientoVigente(): bool','+ riesgoVacancia(): Decimal'],
 'local':['+ zonaAsignada(): Zona'],
 'usuario':['+ autenticar(clave): bool','+ tienePermiso(p): bool','+ centrosAccesibles()'],
 'rol':['+ agregarPermiso(p)','+ permisos(): List'],
 'permiso':['+ clave(): String'],
 'usuario_rol':['+ vigente(): bool'],
 'rol_permiso':['+ otorgado(): Date'],
 'centro_acceso':['+ habilitar()','+ revocar()'],
 'conector_pos':['+ probarConexion(): bool','+ sincronizar()','+ estaActivo(): bool'],
 'registro_pos':['+ montoNeto(): Decimal'],
 'dispositivo_iot':['+ publicarEvento(e)','+ estaEnLinea(): bool','+ calibrar()'],
 'evento_trafico':['+ franjaHoraria(): int'],
 'indicador':['+ calcular(periodo): Decimal'],
 'regla_alerta':['+ evaluar(valor): bool','+ destinatarios(): List'],
 'regla_destinatario':['+ notificar(a)'],
 'modelo_ml':['+ entrenar(datos)','+ predecir(x)','+ metricas(): Map'],
 'alerta':['+ asignar(u)','+ escalar()','+ resolver(u, nota)'],
 'resolucion_alerta':['+ duracion(): int'],
 'prediccion_vacancia':['+ nivelRiesgo(): String','+ generarAcciones()'],
 'accion_retencion':['+ ejecutar()','+ registrarResultado(r)'],
 'recomendacion':['+ aplicable(): bool','+ decidir(u, estado)'],
 'recomendacion_decision':['+ justificacion(): String'],
 'consentimiento':['+ vigente(): bool','+ revocar()'],
 'evento_auditoria':['+ hash(): String'],
 'reporte':['+ generar()','+ exportar(formato)'],
 'notificacion':['+ enviar()','+ marcarLeida()'],
 'preferencia_notificacion':['+ permiteCanal(c): bool'],
 'parametro_sistema':['+ valorTipado()','+ actualizar(v, u)'],
}

def clase(nombre):
    especial = {'modelo_ml':'ModeloML','dispositivo_iot':'DispositivoIoT','conector_pos':'ConectorPos',
                'registro_pos':'RegistroPos'}
    if nombre in especial: return especial[nombre]
    return "".join(p.capitalize() for p in nombre.split('_'))

def cargar(ruta='/tmp/diccionario.json'):
    ents = {e['nombre']: e for e in json.load(open(ruta))}
    rels = []
    for e in ents.values():
        for c in e['campos']:
            if 'FK' not in c['clave']: continue
            base = re.sub(r'_id$','',c['campo'])
            dst = base if base in ents else ALIAS.get(base)
            if not dst: continue
            rels.append({'padre':dst, 'hijo':e['nombre'], 'campo':c['campo'],
                         'opcional':bool(OPCIONAL.search(c['desc'])),
                         'comp':(dst, e['nombre']) in COMPOSICION})
    return ents, rels

def esc(s):
    return (s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
             .replace('"','&quot;'))
