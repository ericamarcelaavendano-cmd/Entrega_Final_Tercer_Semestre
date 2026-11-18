"""Genera la app web de presentación a partir de los resultados del análisis.

Primero ejecuta:  python analisis_desercion.py
Después ejecuta:  python generar_reporte.py
Y abre en el navegador:  app/index.html
"""
from datetime import date
from html import escape
from pathlib import Path

import pandas as pd

BASE = Path(__file__).parent
PROCESSED = BASE / "Data" / "processed"
APP = BASE / "app"
AUTORA = "Erica Avendaño A"
INSTITUCION = "CESDE · Análisis y Desarrollo de Software"
GRAFICOS = "../Data/processed/graficos"  # ruta relativa desde app/ hasta los PNG

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


# ---------------------------------------------------------------------------
# Cálculos
# ---------------------------------------------------------------------------

def calcular(df):
    """Recalcula las cinco preguntas desde el dataset limpio."""
    r = {"total": len(df), "tasa_general": df["desertor"].mean(), "desertores": int(df["desertor"].sum())}
    r["p1"] = (df.groupby("programa").agg(tasa=("desertor", "mean"), estudiantes=("desertor", "size"))
                 .sort_values("tasa", ascending=False))
    r["p2"] = df.groupby("beca").agg(tasa=("desertor", "mean"), estudiantes=("desertor", "size"))
    r["p3"] = (df.groupby("jornada")
                 .agg(promedio=("promedio_acumulado", "mean"), estudiantes=("promedio_acumulado", "size"))
                 .sort_values("promedio"))
    sin_grad = df[df["estado"] != "graduado"]
    r["p4"] = sin_grad.groupby("estado").agg(
        materias=("materias_reprobadas", "mean"), estudiantes=("materias_reprobadas", "size"))
    r["p5"] = (df.groupby("cuartil_asistencia").agg(
        tasa=("desertor", "mean"), asistencia=("asistencia_pct", "mean"), estudiantes=("desertor", "size"))
        .reindex(["Q1", "Q2", "Q3", "Q4"]).dropna())
    return r


# ---------------------------------------------------------------------------
# Piezas de HTML
# ---------------------------------------------------------------------------

def pct(v):
    return f"{v * 100:.1f} %".replace(".", ",")


def num(v, dec=0):
    texto = f"{v:,.{dec}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def tabla(filas, columnas):
    """Tabla con columnas numéricas alineadas a la derecha.

    columnas: lista de (titulo, funcion_que_recibe_la_fila_y_devuelve_html, es_numero)
    """
    cab = "".join(f'<th class="{"n" if n else ""}">{escape(t)}</th>' for t, _, n in columnas)
    cuerpo = ""
    for fila in filas:
        celdas = "".join(f'<td class="{"n" if n else ""}">{f(fila)}</td>' for _, f, n in columnas)
        cuerpo += f"<tr>{celdas}</tr>"
    return f'<div class="tabla-wrap"><table><thead><tr>{cab}</tr></thead><tbody>{cuerpo}</tbody></table></div>'


def barra(valor, maximo, destacado=False):
    """Barra horizontal pequeña dentro de una celda, para leer la tabla de un vistazo."""
    ancho = 0 if maximo == 0 else valor / maximo * 100
    clase = "barra destacada" if destacado else "barra"
    return f'<span class="{clase}"><span style="width:{ancho:.1f}%"></span></span>'


def figura(nombre, titulo, nota):
    if (PROCESSED / "graficos" / nombre).exists():
        return (f'<figure><figcaption><strong>{titulo}</strong><span>{nota}</span></figcaption>'
                f'<img src="{GRAFICOS}/{nombre}" alt="{escape(titulo)}"></figure>')
    return f'<p class="aviso">No se encontró {nombre}. Ejecuta primero analisis_desercion.py.</p>'


def hallazgo(texto):
    return f'<div class="hallazgo"><span class="etiqueta">Hallazgo</span><p>{texto}</p></div>'


def seccion(id_, numero, kicker, titulo, intro, contenido):
    return f"""
<section id="{id_}" class="seccion">
  <div class="contenedor">
    <header class="seccion-cab">
      <span class="numero">{numero}</span>
      <div>
        <p class="kicker">{kicker}</p>
        <h2>{titulo}</h2>
        <p class="intro">{intro}</p>
      </div>
    </header>
    {contenido}
  </div>
</section>"""


# ---------------------------------------------------------------------------
# Estilos: paleta corporativa (marino, pizarra y un acento azul)
# ---------------------------------------------------------------------------

ESTILOS = """
:root{
  --marino:#0b1f3a; --marino-2:#13305a; --acento:#2563eb; --acento-suave:#e8efff;
  --tinta:#0f172a; --texto:#334155; --gris:#64748b; --linea:#e2e8f0; --fondo:#f5f7fa;
  --blanco:#ffffff; --alerta:#b42318; --ok:#0f766e;
  --radio:10px; --sombra:0 1px 2px rgba(15,23,42,.06),0 4px 16px rgba(15,23,42,.05);
  --fuente:"Segoe UI","Inter",system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;font-family:var(--fuente);color:var(--texto);background:var(--fondo);
     line-height:1.6;font-size:16px;-webkit-font-smoothing:antialiased}
h1,h2,h3{color:var(--tinta);line-height:1.2;margin:0;letter-spacing:-.01em}
a{color:var(--acento)}
.contenedor{width:100%;max-width:1120px;margin:0 auto;padding:0 24px}
.kicker{font-size:12px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--acento);margin:0 0 8px}

/* ---------- Portada ---------- */
.hero{min-height:100vh;display:flex;flex-direction:column;color:#dbe4f3;
      background:
        radial-gradient(900px 500px at 85% 10%,rgba(37,99,235,.28),transparent 60%),
        linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px) 0 0/48px 48px,
        linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px) 0 0/48px 48px,
        var(--marino)}
.hero-top{display:flex;justify-content:space-between;align-items:center;padding:28px 0;font-size:14px}
.marca{display:flex;align-items:center;gap:10px;color:#fff;font-weight:600}
.marca i{width:28px;height:28px;border-radius:7px;background:var(--acento);display:grid;place-items:center;
         font-style:normal;font-size:13px}
.hero-top span{color:#8ea3c4}
.hero-cuerpo{flex:1;display:grid;grid-template-columns:1.25fr 1fr;gap:56px;align-items:center;padding:24px 0 48px}
.hero .kicker{color:#7fa7ff}
.hero h1{color:#fff;font-size:clamp(34px,5.2vw,58px);font-weight:700;letter-spacing:-.025em;margin-bottom:20px}
.hero .lead{font-size:19px;color:#b6c4dc;max-width:560px;margin:0 0 36px}
.acciones{display:flex;gap:14px;flex-wrap:wrap}
.boton{display:inline-flex;align-items:center;gap:10px;padding:15px 26px;border-radius:8px;font-weight:600;
       font-size:16px;text-decoration:none;transition:transform .15s ease,background .15s ease}
.boton.primario{background:#fff;color:var(--marino)}
.boton.primario:hover{transform:translateY(-1px);background:#e9eefb}
.boton.secundario{color:#fff;border:1px solid rgba(255,255,255,.25)}
.boton.secundario:hover{background:rgba(255,255,255,.06)}
.panel{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1);border-radius:14px;padding:8px;
       backdrop-filter:blur(4px)}
.panel-kpi{display:flex;justify-content:space-between;align-items:baseline;padding:20px 22px;
           border-bottom:1px solid rgba(255,255,255,.08)}
.panel-kpi:last-child{border-bottom:none}
.panel-kpi span{font-size:14px;color:#8ea3c4}
.panel-kpi b{font-size:30px;color:#fff;font-weight:600;font-variant-numeric:tabular-nums}
.panel-kpi b.alerta{color:#ffb4a8}
.metodo{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid rgba(255,255,255,.1)}
.metodo div{padding:24px 24px 30px 0}
.metodo b{display:block;color:#fff;font-weight:600;margin-bottom:4px}
.metodo small{color:#8ea3c4;font-size:14px}
.metodo em{font-style:normal;color:#7fa7ff;font-size:13px;font-weight:600;display:block;margin-bottom:10px}

/* ---------- Página de análisis ---------- */
.nav{position:sticky;top:0;z-index:10;background:rgba(11,31,58,.97);backdrop-filter:blur(6px)}
.nav .contenedor{display:flex;align-items:center;gap:28px;height:60px;overflow-x:auto}
.nav .marca{white-space:nowrap}
.nav a.link{color:#a9b8d1;text-decoration:none;font-size:14px;white-space:nowrap}
.nav a.link:hover{color:#fff}
.portadilla{background:var(--marino);color:#b6c4dc;padding:56px 0 96px}
.portadilla h1{color:#fff;font-size:clamp(28px,4vw,40px);margin-bottom:12px}
.portadilla .kicker{color:#7fa7ff}
.portadilla p{max-width:640px;margin:0}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-top:-56px}
.kpi{background:var(--blanco);border:1px solid var(--linea);border-radius:var(--radio);padding:22px 24px;box-shadow:var(--sombra)}
.kpi span{display:block;font-size:13px;color:var(--gris);margin-bottom:6px}
.kpi b{font-size:32px;color:var(--tinta);font-weight:650;font-variant-numeric:tabular-nums}
.kpi small{display:block;color:var(--gris);font-size:13px;margin-top:4px}
.kpi.resaltado{border-top:3px solid var(--acento)}
.seccion{padding:72px 0 24px;scroll-margin-top:60px}
.seccion-cab{display:grid;grid-template-columns:72px 1fr;gap:8px;margin-bottom:28px}
.numero{font-size:15px;font-weight:600;color:var(--gris);font-variant-numeric:tabular-nums;padding-top:2px}
.seccion-cab h2{font-size:30px;margin-bottom:10px}
.intro{color:var(--gris);max-width:720px;margin:0}
.bloque{margin-left:80px}
h3{font-size:19px;margin:40px 0 4px}
h3 + .sub{color:var(--gris);font-size:14px;margin:0 0 14px}
.tabla-wrap{overflow-x:auto;background:var(--blanco);border:1px solid var(--linea);border-radius:var(--radio);box-shadow:var(--sombra)}
table{width:100%;border-collapse:collapse;font-size:14px}
th{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--gris);font-weight:600;
   text-align:left;padding:12px 16px;border-bottom:1px solid var(--linea);background:#fbfcfe;white-space:nowrap}
td{padding:12px 16px;border-bottom:1px solid var(--linea);color:var(--tinta);vertical-align:top}
tr:last-child td{border-bottom:none}
tbody tr:hover td{background:#f8faff}
.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
td.just{color:var(--texto);min-width:280px}
.chip{display:inline-block;font-size:12px;padding:2px 9px;border-radius:999px;background:var(--acento-suave);
      color:var(--marino-2);font-weight:600;white-space:nowrap}
.barra{display:inline-block;width:110px;height:6px;background:#eef2f7;border-radius:3px;vertical-align:middle;margin-left:12px}
.barra span{display:block;height:100%;background:#94a3b8;border-radius:3px}
.barra.destacada span{background:var(--acento)}
.hallazgo{display:grid;grid-template-columns:auto 1fr;gap:16px;align-items:start;background:var(--blanco);
          border:1px solid var(--linea);border-left:3px solid var(--acento);border-radius:var(--radio);
          padding:16px 20px;margin:16px 0 0}
.hallazgo p{margin:0;color:var(--tinta)}
.etiqueta{font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--acento);padding-top:3px}
.nota{font-size:14px;color:var(--gris);margin:12px 0 0}
figure{margin:20px 0 0;background:var(--blanco);border:1px solid var(--linea);border-radius:var(--radio);
       padding:20px;box-shadow:var(--sombra)}
figcaption{display:flex;flex-direction:column;margin-bottom:14px}
figcaption strong{color:var(--tinta)}
figcaption span{color:var(--gris);font-size:14px}
figure img{width:100%;height:auto;display:block}
.rejilla{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.tarjeta{background:var(--blanco);border:1px solid var(--linea);border-radius:var(--radio);padding:24px;box-shadow:var(--sombra)}
.tarjeta h3{margin:0 0 10px;font-size:17px}
.tarjeta p{margin:0;font-size:15px}
.tarjeta .kicker{margin-bottom:12px}
.aviso{background:#fff7ed;border:1px solid #fed7aa;padding:12px 16px;border-radius:8px}
footer{margin-top:80px;background:var(--marino);color:#8ea3c4;font-size:14px}
footer .contenedor{display:flex;justify-content:space-between;gap:16px;padding:32px 24px;flex-wrap:wrap}
footer a{color:#fff;text-decoration:none}

@media (max-width:900px){
  .hero-cuerpo{grid-template-columns:1fr;gap:36px}
  .metodo{grid-template-columns:repeat(2,1fr)}
  .kpis{grid-template-columns:repeat(2,1fr)}
  .rejilla{grid-template-columns:1fr}
  .bloque{margin-left:0}
  .seccion-cab{grid-template-columns:1fr}
}
@media (max-width:520px){
  .contenedor{padding:0 16px}
  .kpis,.metodo{grid-template-columns:1fr}
  .hero-top span{display:none}
}
@media print{
  .nav{position:static} .hero{min-height:auto} .kpi,figure,.tabla-wrap{box-shadow:none}
}
"""


def pagina(titulo, cuerpo):
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title>
<style>{ESTILOS}</style>
</head>
<body>
{cuerpo}
</body>
</html>"""


# ---------------------------------------------------------------------------
# Página 1: portada
# ---------------------------------------------------------------------------

def portada(r, n_decisiones):
    hoy = date.today()
    fecha = f"{MESES[hoy.month - 1].capitalize()} {hoy.year}"
    cuerpo = f"""
<main class="hero">
  <div class="contenedor hero-top">
    <div class="marca"><i>RE</i>Retención Estudiantil</div>
    <span>{INSTITUCION} · {fecha}</span>
  </div>

  <div class="contenedor hero-cuerpo">
    <div>
      <p class="kicker">Informe de análisis de datos</p>
      <h1>Calidad de datos para la retención estudiantil</h1>
      <p class="lead">Auditoría, limpieza y análisis de los registros académicos para identificar
      los factores asociados a la deserción y orientar estrategias de retención temprana.</p>
      <div class="acciones">
        <a class="boton primario" href="analisis.html">Ver el análisis <span aria-hidden="true">→</span></a>
        <a class="boton secundario" href="analisis.html#preguntas">Ir a los resultados</a>
      </div>
    </div>

    <aside class="panel" aria-label="Cifras principales">
      <div class="panel-kpi"><span>Estudiantes analizados</span><b>{num(r['total'])}</b></div>
      <div class="panel-kpi"><span>Tasa general de deserción</span><b class="alerta">{pct(r['tasa_general'])}</b></div>
      <div class="panel-kpi"><span>Decisiones de limpieza</span><b>{n_decisiones}</b></div>
      <div class="panel-kpi"><span>Preguntas respondidas</span><b>5</b></div>
    </aside>
  </div>

  <div class="contenedor">
    <div class="metodo">
      <div><em>01</em><b>Conocer</b><small>Diccionario de las 23 columnas</small></div>
      <div><em>02</em><b>Auditar</b><small>Seis tipos de problema de calidad</small></div>
      <div><em>03</em><b>Limpiar</b><small>Decisiones registradas y justificadas</small></div>
      <div><em>04</em><b>Analizar</b><small>Cinco preguntas de la institución</small></div>
    </div>
  </div>
</main>"""
    return pagina("Retención Estudiantil · Informe", cuerpo)


# ---------------------------------------------------------------------------
# Página 2: análisis
# ---------------------------------------------------------------------------

def analisis(r, decisiones):
    p1, p2, p3, p4, p5 = r["p1"], r["p2"], r["p3"], r["p4"], r["p5"]

    # --- Resumen ---
    resumen = f"""
<div class="contenedor">
  <div class="kpis">
    <div class="kpi resaltado"><span>Estudiantes en el dataset limpio</span><b>{num(r['total'])}</b><small>Registros confiables para el análisis</small></div>
    <div class="kpi"><span>Desertores</span><b>{num(r['desertores'])}</b><small>Estado igual a «desertor»</small></div>
    <div class="kpi"><span>Tasa general de deserción</span><b>{pct(r['tasa_general'])}</b><small>Línea base de comparación</small></div>
    <div class="kpi"><span>Decisiones de limpieza</span><b>{len(decisiones)}</b><small>Registradas en decisiones.csv</small></div>
  </div>
</div>"""

    # --- Calidad ---
    calidad = f"""<div class="bloque">
  {figura("mapa_faltantes.png", "Mapa de faltantes del dataset original",
          "Cada franja marca una celda vacía. Los guiones y el valor 999 no aparecen: son faltantes disfrazados.")}
  {figura("distribuciones_antes_despues.png", "Distribuciones antes y después de la limpieza",
          "Desaparecen los promedios fuera de la escala 0 a 5 y las edades imposibles.")}
</div>"""

    # --- Decisiones ---
    filas = decisiones.to_dict("records")
    t_dec = tabla(filas, [
        ("Paso", lambda f: f'<span class="chip">{escape(str(f["paso"]))}</span>', False),
        ("Columna", lambda f: escape(str(f["columna"])), False),
        ("Acción", lambda f: escape(str(f["accion"])), False),
        ("Filas", lambda f: num(f["filas_afectadas"]), True),
        ("Justificación", lambda f: f'<span class="just">{escape(str(f["justificacion"]))}</span>', False),
    ])
    bloque_dec = f'<div class="bloque">{t_dec}</div>'

    # --- Preguntas ---
    max1 = p1["tasa"].max()
    t1 = tabla(list(p1.itertuples()), [
        ("Programa", lambda f: escape(f.Index), False),
        ("Estudiantes", lambda f: num(f.estudiantes), True),
        ("Tasa de deserción", lambda f: pct(f.tasa) + barra(f.tasa, max1, f.tasa == max1), True),
    ])
    max2 = p2["tasa"].max()
    t2 = tabla(list(p2.itertuples()), [
        ("Beca", lambda f: escape(str(f.Index)), False),
        ("Estudiantes", lambda f: num(f.estudiantes), True),
        ("Tasa de deserción", lambda f: pct(f.tasa) + barra(f.tasa, max2, f.tasa == max2), True),
    ])
    min3, max3 = p3["promedio"].min(), p3["promedio"].max()
    t3 = tabla(list(p3.itertuples()), [
        ("Jornada", lambda f: escape(f.Index), False),
        ("Estudiantes", lambda f: num(f.estudiantes), True),
        ("Promedio acumulado", lambda f: num(f.promedio, 2) + barra(f.promedio, max3, f.promedio == min3), True),
    ])
    max4 = p4["materias"].max()
    t4 = tabla(list(p4.itertuples()), [
        ("Estado", lambda f: escape(f.Index.capitalize()), False),
        ("Estudiantes", lambda f: num(f.estudiantes), True),
        ("Materias reprobadas (promedio)", lambda f: num(f.materias, 2) + barra(f.materias, max4, f.materias == max4), True),
    ])
    max5 = p5["tasa"].max()
    t5 = tabla(list(p5.itertuples()), [
        ("Cuartil", lambda f: escape(str(f.Index)), False),
        ("Asistencia promedio", lambda f: num(f.asistencia, 1) + " %", True),
        ("Estudiantes", lambda f: num(f.estudiantes), True),
        ("Tasa de deserción", lambda f: pct(f.tasa) + barra(f.tasa, max5, f.tasa == max5), True),
    ])

    beca_menor = p2["tasa"].idxmin()
    diferencia = (p2["tasa"].max() - p2["tasa"].min()) * 100
    q1, q4 = p5["tasa"].iloc[0], p5["tasa"].iloc[-1]
    tendencia = "aumenta" if q1 > q4 else "no aumenta"
    desertor = p4.loc["desertor", "materias"] if "desertor" in p4.index else float("nan")
    activo = p4.loc["activo", "materias"] if "activo" in p4.index else float("nan")

    preguntas = f"""<div class="bloque">
  <h3>1. ¿Qué programa presenta la tasa de deserción más alta?</h3>
  <p class="sub">Tasa de deserción y tamaño de cada programa.</p>
  {t1}
  {hallazgo(f"<b>{escape(p1.index[0])}</b> presenta la tasa más alta: {pct(p1['tasa'].iloc[0])} entre {num(p1['estudiantes'].iloc[0])} estudiantes, frente a una tasa general de {pct(r['tasa_general'])}.")}
  {figura("tasa_desercion_por_programa.png", "Tasa de deserción por programa", "Proporción de desertores en cada programa académico.")}

  <h3>2. ¿Hay diferencia entre becados y no becados?</h3>
  <p class="sub">Comparación de la tasa de deserción según beca.</p>
  {t2}
  {hallazgo(f"La deserción es menor en el grupo beca = <b>{escape(str(beca_menor))}</b>, con una diferencia de {num(diferencia, 1)} puntos porcentuales. Es una asociación: no prueba que la beca cause la permanencia.")}

  <h3>3. ¿Qué jornada tiene el menor promedio acumulado?</h3>
  <p class="sub">Promedio acumulado en escala de 0 a 5.</p>
  {t3}
  {hallazgo(f"<b>{escape(p3.index[0])}</b> registra el menor promedio acumulado: {num(p3['promedio'].iloc[0], 2)}.")}

  <h3>4. Materias reprobadas: desertores frente a activos</h3>
  <p class="sub">Se excluyen los graduados porque no pertenecen a ninguno de los dos grupos comparados.</p>
  {t4}
  {hallazgo(f"Los desertores reprobaron en promedio <b>{num(desertor, 2)}</b> materias, frente a {num(activo, 2)} de los activos.")}

  <h3>5. ¿La deserción aumenta conforme baja la asistencia?</h3>
  <p class="sub">Q1 agrupa la asistencia más baja y Q4 la más alta. Cada cuartil tiene un tamaño parecido.</p>
  {t5}
  {hallazgo(f"La deserción <b>{tendencia}</b> cuando baja la asistencia: {pct(q1)} en Q1 frente a {pct(q4)} en Q4. El patrón muestra asociación, no causa.")}
  {figura("tasa_desercion_por_asistencia.png", "Tasa de deserción por cuartil de asistencia", "Q1 = asistencia más baja · Q4 = asistencia más alta.")}
</div>"""

    reflexiones = """<div class="bloque rejilla">
  <div class="tarjeta"><p class="kicker">Reflexión 1</p><h3>Asociación no es causalidad</h3>
    <p>Que los becados deserten menos no prueba que la beca los retenga. Las becas suelen darse a
    estudiantes con buen rendimiento, que ya tenían menos riesgo. Para hablar de causa habría que
    comparar grupos iguales en todo, excepto en la beca.</p></div>
  <div class="tarjeta"><p class="kicker">Reflexión 2</p><h3>motivo_retiro no sirve para predecir</h3>
    <p>Solo se conoce después de que el estudiante deserta. Usarlo en un modelo sería predecir con
    información del futuro, que nunca estaría disponible a tiempo.</p></div>
  <div class="tarjeta"><p class="kicker">Reflexión 3</p><h3>Variables sensibles</h3>
    <p>Género, estrato y ciudad pueden reflejar desigualdades sociales. Las alertas deben basarse en
    señales académicas, como la asistencia, y estas variables usarse solo para vigilar que el apoyo sea justo.</p></div>
</div>"""

    cuerpo = f"""
<nav class="nav"><div class="contenedor">
  <a class="marca" href="index.html" style="text-decoration:none"><i>RE</i>Retención Estudiantil</a>
  <a class="link" href="#calidad">Calidad</a>
  <a class="link" href="#decisiones">Decisiones</a>
  <a class="link" href="#preguntas">Resultados</a>
  <a class="link" href="#reflexiones">Reflexiones</a>
</div></nav>

<header class="portadilla"><div class="contenedor">
  <p class="kicker">Informe de análisis</p>
  <h1>Factores asociados a la deserción estudiantil</h1>
  <p>Resultados obtenidos sobre el dataset limpio. Cada cifra va acompañada del número de estudiantes
  del grupo, porque una tasa sin su tamaño no se puede interpretar.</p>
</div></header>

{resumen}
{seccion("calidad", "01", "Diagnóstico", "Calidad de los datos originales",
         "Antes de limpiar se revisó el dataset sin modificarlo, para distinguir nulos reales, faltantes disfrazados, valores imposibles, duplicados, errores tipográficos y formatos inconsistentes.", calidad)}
{seccion("decisiones", "02", "Limpieza", "Decisiones de limpieza",
         "Cada cambio quedó registrado con el número de filas afectadas y su justificación, para que cualquier persona pueda revisar el proceso.", bloque_dec)}
{seccion("preguntas", "03", "Resultados", "Las cinco preguntas de la institución",
         "Respuestas calculadas con groupby() y agg() sobre el dataset limpio.", preguntas)}
{seccion("reflexiones", "04", "Alcance", "Lo que los datos no dicen",
         "Tres límites que deben tenerse en cuenta antes de tomar decisiones con estos resultados.", reflexiones)}

<footer><div class="contenedor">
  <span>{AUTORA} · {INSTITUCION}</span>
  <span>Datos sintéticos generados para el taller · <a href="index.html">Volver al inicio</a></span>
</div></footer>"""
    return pagina("Análisis de deserción · Informe", cuerpo)


def main():
    df = pd.read_csv(PROCESSED / "dataset_limpio.csv")
    decisiones = pd.read_csv(PROCESSED / "decisiones.csv")
    r = calcular(df)

    APP.mkdir(exist_ok=True)
    (APP / "index.html").write_text(portada(r, len(decisiones)), encoding="utf-8")
    (APP / "analisis.html").write_text(analisis(r, decisiones), encoding="utf-8")
    print("App generada. Abre app/index.html en el navegador.")


if __name__ == "__main__":
    main()
