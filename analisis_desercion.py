from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)

RAW = Path(__file__).parent / "Data" / "raw" / "datos_estudiantes.csv"
PROCESSED = Path(__file__).parent / "Data" / "processed"
GRAFICOS = PROCESSED / "graficos"

# Valores válidos de cada columna categórica (la forma correcta de escribirlos).
VALIDOS = {
    "programa": ["Administración de Empresas", "Contaduría Pública", "Derecho", "Psicología",
                 "Ingeniería de Sistemas", "Ingeniería Industrial", "Enfermería", "Diseño Gráfico"],
    "jornada": ["Diurna", "Nocturna", "Fin de semana"],
    "genero": ["Femenino", "Masculino"],
    "ciudad_procedencia": ["Bogotá", "Medellín", "Cali", "Bucaramanga", "Rionegro",
                           "Barranquilla", "Otra ciudad"],
}

DECISIONES = []


def registrar(paso, columna, accion, filas, justificacion):
    """Guarda una decisión para la tabla de decisiones. Ya está escrita: solo úsala."""
    DECISIONES.append({
        "paso": paso, "columna": columna, "accion": accion,
        "filas_afectadas": int(filas), "justificacion": justificacion,
    })


def titulo(texto):
    """Imprime un título para separar cada paso en la terminal."""
    print("\n" + "=" * 70)
    print(texto)
    print("=" * 70)


def explorar(df):
    """Paso 1 del Word: primera mirada al dataset.

    Muestra la forma, los tipos y los nulos de cada columna, las estadísticas
    numéricas, y los valores de las columnas programa, jornada, genero y estado.
    Pregunta: ¿alguna columna numérica aparece como texto? ¿Por qué crees que pasa?
    Respuesta: asistencia_pct y horas_trabajo_semana llegan como texto, porque
    basta una celda con '%' o '-' para que pandas trate toda la columna como texto.
    """
    titulo("PASO 1: PRIMERA MIRADA AL DATASET")

    print("\nForma del dataset (filas, columnas):")
    print(df.shape)

    print("\nTipos de datos y nulos:")
    df.info()

    print("\nEstadísticas numéricas:")
    print(df.describe())

    print("\nValores de las columnas categóricas:")
    for col in ["programa", "jornada", "genero", "ciudad_procedencia", "estado"]:
        print(f"\n>> {col}")
        print(df[col].value_counts(dropna=False))
        print("Valores únicos:", df[col].unique().tolist())


def auditar(df):
    """Paso 2 del Word: buscar problemas sin corregirlos todavía.

    Revisa: nulos reales, faltantes disfrazados ('-', 999), valores imposibles
    (edad, promedio, horas), duplicados y formatos de fecha.
    Pregunta: ¿cuál de estos problemas afecta más el análisis? ¿Por qué?
    Respuesta: los formatos (asistencia como texto) y los imposibles (promedios de 0 a 100),
    porque impiden calcular la pregunta 5 o cambian el promedio por jornada de la pregunta 3.
    """
    titulo("PASO 2: AUDITORÍA DE CALIDAD (sin corregir nada)")

    print("\n--- Nulos reales por columna ---")
    nulos = df.isnull().sum()
    print(nulos[nulos > 0])

    print("\n--- Faltantes disfrazados ---")
    print("Guiones en asistencia_pct:      ", (df["asistencia_pct"] == "-").sum())
    print("Guiones en horas_trabajo_semana:", (df["horas_trabajo_semana"] == "-").sum())
    print("Valores 999 en distancia_km:    ", (df["distancia_km"] == 999).sum())

    # Copias temporales en número: solo sirven para contar, df no cambia.
    edad = pd.to_numeric(df["edad"], errors="coerce")
    promedio = pd.to_numeric(df["promedio_acumulado"], errors="coerce")
    horas = pd.to_numeric(df["horas_trabajo_semana"], errors="coerce")

    print("\n--- Valores imposibles ---")
    print("Edades fuera de 15 a 60:    ", ((edad < 15) | (edad > 60)).sum())
    print("Promedios mayores a 5:      ", (promedio > 5).sum())
    print("Horas de trabajo mayores a 100:", (horas > 100).sum())

    print("\n--- Duplicados ---")
    print("Filas idénticas a una anterior:", df.duplicated().sum())

    print("\n--- Formatos inconsistentes ---")
    print("Asistencias con símbolo %:   ", df["asistencia_pct"].str.contains("%", regex=False).sum())
    print("Fechas en formato DD/MM/AAAA:", df["fecha_matricula"].str.contains("/", regex=False).sum())


def convertir_numericos(df):
    """Paso 3 del Word: columnas que deberían ser numéricas, pero llegan como texto.

    Pistas: quitar el símbolo % con str.replace; reemplazar '-' por nulo;
    convertir con pd.to_numeric(..., errors="coerce"); reemplazar 999 por nulo en distancia_km.
    Registra cada conversión con registrar().
    """
    # asistencia_pct: primero cuento, después transformo (así no pierdo el registro).
    con_pct = df["asistencia_pct"].str.contains("%", regex=False).sum()
    guiones = (df["asistencia_pct"] == "-").sum()
    df["asistencia_pct"] = df["asistencia_pct"].str.replace("%", "", regex=False)
    df["asistencia_pct"] = pd.to_numeric(df["asistencia_pct"].replace("-", np.nan), errors="coerce")
    registrar("numericos", "asistencia_pct", "quitar símbolo %", con_pct,
              "El % convierte la columna en texto y no deja calcular promedios ni cuartiles.")
    registrar("numericos", "asistencia_pct", "guion a nulo y convertir a número", guiones,
              "El guion significa 'sin dato'; como nulo real pandas lo reconoce y no lo cuenta como valor.")

    # horas_trabajo_semana
    guiones = (df["horas_trabajo_semana"] == "-").sum()
    df["horas_trabajo_semana"] = pd.to_numeric(df["horas_trabajo_semana"].replace("-", np.nan), errors="coerce")
    registrar("numericos", "horas_trabajo_semana", "guion a nulo y convertir a número", guiones,
              "El guion es un faltante disfrazado; se trata en el paso 8 según si el estudiante trabaja.")

    # distancia_km
    es_999 = df["distancia_km"] == 999
    df.loc[es_999, "distancia_km"] = np.nan
    registrar("numericos", "distancia_km", "999 a nulo", es_999.sum(),
              "999 es un código de 'sin dato'; dejarlo inflaría el promedio de distancia.")
    return df


def unificar_categorias(df):
    """Paso 4 del Word: errores tipográficos en columnas categóricas.

    Pistas: primero df[col].str.strip().str.lower(); después .replace(diccionario)
    con las variantes que encontraste con value_counts(). Los valores correctos están en VALIDOS.
    Pregunta: ¿qué variantes son el mismo valor? ¿Hay alguna que no debas unificar?
    Respuesta: 'M' y 'F' son abreviaturas de Masculino y Femenino. 'Otra ciudad' NO se
    une con ninguna ciudad, porque agrupa lugares distintos.
    """
    # Diccionario de variantes: claves en minúscula (la columna ya pasó por lower()).
    variantes = {
        "programa": {
            "administración de empresas": "Administración de Empresas",
            "contaduría pública": "Contaduría Pública",
            "derecho": "Derecho",
            "psicología": "Psicología", "psicologia": "Psicología",
            "ingeniería de sistemas": "Ingeniería de Sistemas",
            "ingenieria de sistemas": "Ingeniería de Sistemas",
            "ingeniería industrial": "Ingeniería Industrial",
            "enfermería": "Enfermería",
            "diseño gráfico": "Diseño Gráfico",
        },
        "jornada": {"diurna": "Diurna", "nocturna": "Nocturna", "fin de semana": "Fin de semana"},
        "genero": {"femenino": "Femenino", "f": "Femenino", "masculino": "Masculino", "m": "Masculino"},
        "ciudad_procedencia": {
            "bogotá": "Bogotá", "bogota": "Bogotá",
            "medellín": "Medellín", "medellin": "Medellín",
            "cali": "Cali", "bucaramanga": "Bucaramanga", "rionegro": "Rionegro",
            "barranquilla": "Barranquilla", "otra ciudad": "Otra ciudad",
        },
    }

    for col, diccionario in variantes.items():
        antes = df[col].copy()
        df[col] = df[col].str.strip().str.lower().replace(diccionario)
        # Cuento las filas que cambiaron (los nulos no cuentan como cambio).
        cambiaron = (antes != df[col]) & antes.notna()
        registrar("categorias", col, "strip, lower y diccionario de variantes", cambiaron.sum(),
                  "La misma categoría escrita de varias formas se contaría como grupos distintos.")

        no_validos = df[col].dropna()[~df[col].dropna().isin(VALIDOS[col])]
        if len(no_validos) > 0:
            print(f"Atención: {col} tiene valores fuera de VALIDOS: {no_validos.unique().tolist()}")
    return df


def convertir_fechas(df):
    """Paso 5 del Word: fechas escritas en dos formatos.

    Pista: intenta el formato AAAA-MM-DD y luego DD/MM/AAAA, cada uno con errors="coerce",
    y junta los resultados con fillna(). Registra cuántas fechas tenían el segundo formato.
    """
    formato_dmy = df["fecha_matricula"].str.contains("/", regex=False).sum()
    iso = pd.to_datetime(df["fecha_matricula"], format="%Y-%m-%d", errors="coerce")
    dmy = pd.to_datetime(df["fecha_matricula"], format="%d/%m/%Y", errors="coerce")
    df["fecha_matricula"] = iso.fillna(dmy)
    registrar("fechas", "fecha_matricula", "convertir con dos formatos y unir con fillna", formato_dmy,
              "Con un solo formato, las fechas DD/MM/AAAA quedarían vacías.")
    return df


def eliminar_duplicados(df):
    """Paso 6 del Word: filas repetidas.

    Pregunta: ¿podrían existir dos estudiantes distintos con todos los datos iguales?
    Respuesta: no, porque id_estudiante es único. Si toda la fila coincide, incluido el id,
    es el mismo registro copiado dos veces.
    """
    duplicados = df.duplicated().sum()
    df = df.drop_duplicates().reset_index(drop=True)
    registrar("duplicados", "todas", "eliminar filas repetidas", duplicados,
              "Tienen el mismo id_estudiante: contarlas dos veces altera tasas y promedios.")
    return df


def tratar_faltantes(df):
    """Paso 7 del Word: decidir qué hacer con los nulos reales.

    Preguntas:
    - ¿Puedes inventar una nota? ¿Qué pasa si imputas el promedio?
    - Para ciudad o tipo de colegio, ¿conviene eliminar la fila o marcar el dato como 'Sin dato'?
    - motivo_retiro tiene muchos nulos. ¿Son errores? (Pista: ¿para quiénes aplica esa columna?)
    """
    # promedio_acumulado: una nota no se inventa, se elimina la fila.
    nulos = df["promedio_acumulado"].isnull().sum()
    df = df.dropna(subset=["promedio_acumulado"]).reset_index(drop=True)
    registrar("faltantes", "promedio_acumulado", "eliminar filas", nulos,
              "Una nota no se puede inventar; imputarla cambiaría el promedio por jornada.")

    # ciudad y tipo de colegio: se marca, no se elimina (el resto de la fila sí sirve).
    for col in ["ciudad_procedencia", "tipo_colegio"]:
        nulos = df[col].isnull().sum()
        df[col] = df[col].fillna("Sin dato")
        registrar("faltantes", col, "reemplazar por 'Sin dato'", nulos,
                  "Eliminar la fila perdería sus demás datos; inventar el dato sería falso.")

    # motivo_retiro: el nulo es esperado. No se toca.
    registrar("faltantes", "motivo_retiro", "dejar los nulos", 0,
              "Solo aplica a desertores; en activos y graduados el nulo es correcto.")
    return df


def tratar_imposibles(df):
    """Paso 8 del Word: valores que no pueden existir.

    Preguntas:
    - La escala del promedio es de 0 a 5. ¿Qué harías con un 45?
    - Una edad de 150 años es un error. ¿Qué valor pondrías en su lugar?
    - Si el estudiante no trabaja, ¿cuántas horas de trabajo tiene? ¿Cómo lo aplicas en código?
    """
    # Promedio mayor a 5: no sé con certeza la escala original, así que no la adivino.
    imposibles = df["promedio_acumulado"] > 5
    df = df[~imposibles].reset_index(drop=True)
    registrar("imposibles", "promedio_acumulado", "eliminar promedios mayores a 5", imposibles.sum(),
              "Fuera de la escala 0 a 5; convertirlos sería suponer una escala que no conozco.")

    # Edad fuera de 15 a 60: se marca como nulo y se reemplaza por la mediana.
    df["edad"] = df["edad"].astype(float)  # para poder guardar NaN en la columna
    fuera = (df["edad"] < 15) | (df["edad"] > 60)
    df.loc[fuera, "edad"] = np.nan
    mediana_edad = df["edad"].median()  # se calcula con las edades reales
    df["edad"] = df["edad"].fillna(mediana_edad)
    registrar("imposibles", "edad", f"fuera de 15 a 60 a mediana ({mediana_edad:.0f})", fuera.sum(),
              "Son errores de registro; la mediana no se afecta por los extremos.")

    # Horas: si no trabaja, sus horas son 0.
    no_trabaja = df["trabaja"].str.strip().str.lower() == "no"
    regla_cero = no_trabaja & df["horas_trabajo_semana"].isnull()
    df.loc[regla_cero, "horas_trabajo_semana"] = 0
    registrar("imposibles", "horas_trabajo_semana", "nulo a 0 si no trabaja", regla_cero.sum(),
              "Quien no trabaja tiene 0 horas de trabajo; no es un dato perdido.")

    # Horas mayores a 100: imposible en la práctica. Nulo y mediana de quienes trabajan.
    exceso = df["horas_trabajo_semana"] > 100
    df.loc[exceso, "horas_trabajo_semana"] = np.nan
    mediana_horas = df.loc[~no_trabaja, "horas_trabajo_semana"].median()
    faltan = df["horas_trabajo_semana"].isnull()
    df.loc[faltan, "horas_trabajo_semana"] = mediana_horas
    registrar("imposibles", "horas_trabajo_semana",
              f"mayores a 100 y nulos restantes a mediana de quienes trabajan ({mediana_horas:.0f})",
              faltan.sum(),
              "Más de 100 horas no es creíble; la mediana de los que trabajan es el valor típico del grupo.")
    return df


def crear_variables(df):
    """Paso 9 del Word: variables nuevas para el análisis.

    Pregunta: ¿por qué conviene usar cuartiles y no valores exactos de asistencia?
    Respuesta: con valores exactos habría decenas de grupos muy pequeños; los cuartiles
    forman cuatro grupos de tamaño parecido, así las tasas se pueden comparar.
    """
    df["desertor"] = df["estado"].eq("desertor")
    registrar("variables", "desertor", "crear True/False desde estado", df["desertor"].sum(),
              "El promedio de True/False da directamente la tasa de deserción.")

    df["cuartil_asistencia"] = pd.qcut(df["asistencia_pct"], 4, labels=["Q1", "Q2", "Q3", "Q4"])
    registrar("variables", "cuartil_asistencia", "dividir asistencia en 4 grupos con qcut",
              df["cuartil_asistencia"].notna().sum(),
              "Grupos de tamaño parecido para comparar la deserción; Q1 es la asistencia más baja.")
    return df


def guardar_grafico(nombre):
    """Guarda la figura actual en la carpeta de gráficos, la muestra y la cierra."""
    GRAFICOS.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(GRAFICOS / nombre, bbox_inches="tight", dpi=120)
    plt.show()
    plt.close()


def grafico_faltantes(df):
    """Gráfico 1: mapa de faltantes del dataset original."""
    plt.figure(figsize=(12, 6))
    sns.heatmap(df.isnull(), cbar=False, yticklabels=False, cmap=["#e2e8f0", "#0b1f3a"])
    plt.title("Mapa de faltantes del dataset original")
    guardar_grafico("mapa_faltantes.png")


def grafico_distribuciones(antes, despues):
    """Gráfico 2: boxplots de promedio_acumulado y edad, antes y después de limpiar."""
    fig, ejes = plt.subplots(2, 2, figsize=(12, 8))
    sns.boxplot(x=antes["promedio_acumulado"], ax=ejes[0, 0], color="#93b4f5")
    ejes[0, 0].set_title("promedio_acumulado (antes)")
    sns.boxplot(x=despues["promedio_acumulado"], ax=ejes[0, 1], color="#93b4f5")
    ejes[0, 1].set_title("promedio_acumulado (después)")
    sns.boxplot(x=antes["edad"], ax=ejes[1, 0], color="#93b4f5")
    ejes[1, 0].set_title("edad (antes)")
    sns.boxplot(x=despues["edad"], ax=ejes[1, 1], color="#93b4f5")
    ejes[1, 1].set_title("edad (después)")
    guardar_grafico("distribuciones_antes_despues.png")


def grafico_tasa_programa(df):
    """Gráfico 3: tasa de deserción por programa."""
    tasa = df.groupby("programa")["desertor"].mean().sort_values(ascending=False)
    plt.figure(figsize=(10, 5))
    tasa.plot(kind="bar", color="#2563eb")
    plt.title("Tasa de deserción por programa")
    plt.ylabel("Proporción de desertores")
    plt.xticks(rotation=45, ha="right")
    guardar_grafico("tasa_desercion_por_programa.png")


def grafico_tasa_asistencia(df):
    """Gráfico 4: tasa de deserción por cuartil de asistencia."""
    tasa = df.groupby("cuartil_asistencia", observed=True)["desertor"].mean()
    plt.figure(figsize=(7, 5))
    tasa.plot(kind="bar", color="#2563eb")
    plt.title("Tasa de deserción por cuartil de asistencia")
    plt.xlabel("Cuartil (Q1 = asistencia más baja)")
    plt.ylabel("Proporción de desertores")
    plt.xticks(rotation=0)
    guardar_grafico("tasa_desercion_por_asistencia.png")


def responder_preguntas(df):
    """Paso 10 del Word: las cinco preguntas de la institución.

    Cada respuesta incluye el número de estudiantes por grupo, porque sin ese dato
    una tasa no se puede interpretar.
    """
    titulo("PASO 10: LAS CINCO PREGUNTAS")
    print(f"Tasa general de deserción: {df['desertor'].mean():.1%} de {len(df)} estudiantes")

    print("\nPregunta 1: ¿Qué programa presenta la tasa de deserción más alta?")
    p1 = (df.groupby("programa")
            .agg(tasa=("desertor", "mean"), estudiantes=("desertor", "size"))
            .sort_values("tasa", ascending=False))
    print(p1.round(3))
    print(f"Respuesta: {p1.index[0]}, con {p1['tasa'].iloc[0]:.1%} de {p1['estudiantes'].iloc[0]} estudiantes.")

    print("\nPregunta 2: ¿Hay diferencia en la deserción entre becados y no becados?")
    p2 = df.groupby("beca").agg(tasa=("desertor", "mean"), estudiantes=("desertor", "size"))
    print(p2.round(3))

    print("\nPregunta 3: ¿Qué jornada tiene el menor promedio acumulado?")
    p3 = (df.groupby("jornada")
            .agg(promedio=("promedio_acumulado", "mean"), estudiantes=("promedio_acumulado", "size"))
            .sort_values("promedio"))
    print(p3.round(2))
    print(f"Respuesta: {p3.index[0]}, con promedio {p3['promedio'].iloc[0]:.2f}.")

    print("\nPregunta 4: Materias reprobadas, desertores frente a activos (sin graduados)")
    sin_graduados = df[df["estado"] != "graduado"]
    p4 = sin_graduados.groupby("estado").agg(
        materias_reprobadas=("materias_reprobadas", "mean"), estudiantes=("materias_reprobadas", "size"))
    print(p4.round(2))

    print("\nPregunta 5: ¿La deserción aumenta conforme baja la asistencia?")
    p5 = df.groupby("cuartil_asistencia", observed=True).agg(
        tasa=("desertor", "mean"),
        asistencia_promedio=("asistencia_pct", "mean"),
        estudiantes=("desertor", "size"))
    print(p5.round(3))


def guardar(df):
    """Paso 11 del Word: guardar el dataset limpio y la tabla de decisiones. Ya está escrito."""
    PROCESSED.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED / "dataset_limpio.csv", index=False)
    pd.DataFrame(DECISIONES).to_csv(PROCESSED / "decisiones.csv", index=False)
    print(f"\nDataset limpio guardado: {df.shape[0]} filas, {df.shape[1]} columnas.")


def main():
    original = pd.read_csv(RAW)
    df = original.copy()

    explorar(df)
    auditar(df)
    grafico_faltantes(df)

    df = convertir_numericos(df)
    df = unificar_categorias(df)
    df = convertir_fechas(df)
    df = eliminar_duplicados(df)
    df = tratar_faltantes(df)
    df = tratar_imposibles(df)
    df = crear_variables(df)

    grafico_distribuciones(original, df)
    grafico_tasa_programa(df)
    grafico_tasa_asistencia(df)

    responder_preguntas(df)
    print("\nTabla de decisiones:")
    print(pd.DataFrame(DECISIONES))
    guardar(df)


if __name__ == "__main__":
    main()
