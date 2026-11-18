# Taller práctico proyecto integrador: calidad de datos para la retención estudiantil

Una institución de educación superior quiere entender qué factores están asociados a la deserción, para diseñar estrategias de retención tempranas. Antes de responder preguntas de análisis, el equipo de datos debe garantizar que la información sea confiable. Este taller trabaja justo ese paso: auditar, limpiar y documentar los datos, y después responder cinco preguntas con esos datos limpios.

Los datos son sintéticos. Fueron generados para el taller y no corresponden a estudiantes reales.

## Requisitos

- Python 3.10 o superior
- Git
- Lo visto en los talleres de Pandas y de limpieza de datos

## Cómo empezar

1. Clona el repositorio y entra a la carpeta del proyecto:

   ```
   git clone <URL-DEL-REPOSITORIO>
   cd <NOMBRE-DE-LA-CARPETA>
   ```

2. Crea y activa un ambiente virtual. Las instrucciones para Windows y Mac/Linux están en `LEEME_ambiente.txt`.

3. Instala las librerías:

   ```
   pip install -r requirements.txt
   ```

4. Ejecuta el script:

   ```
   python analisis_desercion.py
   ```

Ejecuta el comando desde la carpeta del proyecto.

## Estructura del proyecto

```
proyecto/
├── analisis_desercion.py   Script principal. Tiene un TODO por cada paso.
├── requirements.txt        Versiones de las librerías.
├── LEEME_ambiente.txt      Pasos para crear el ambiente virtual.
├── README.md               Este archivo.
├── .gitignore              Archivos que Git no debe subir.
└── Data/
    ├── raw/
    │   └── datos_estudiantes.csv   Dataset original. No lo modifiques.
    └── processed/
        ├── .gitkeep                Mantiene la carpeta en el repositorio.
        ├── dataset_limpio.csv      Lo genera el script. No se sube (está en .gitignore).
        ├── decisiones.csv          Lo genera el script. Sí se sube.
        └── graficos/               Lo genera el script. Sí se sube.
```

Lo que genera el script (`dataset_limpio.csv`, `decisiones.csv` y `graficos/`) aparece en `Data/processed/` al ejecutarlo. Los dos últimos se suben al repositorio, porque son parte de la entrega.

## Qué debes hacer

Completa los TODO de `analisis_desercion.py` en orden. Cada función tiene un docstring con preguntas: respóndelas antes de escribir el código. Cada decisión que tomes debe quedar registrada con `registrar()`.

Cuando termines, el script debe producir:

- `Data/processed/dataset_limpio.csv`: el dataset limpio.
- `Data/processed/decisiones.csv`: la tabla de decisiones.
- `Data/processed/graficos/`: los cuatro gráficos.

La guía del taller (`Taller_Retencion_Estudiantil.docx`) explica cada método antes de usarlo, con ejemplos y errores frecuentes.

## Entrega

Sube tu código completo al repositorio y envía el enlace por el formulario de entrega. La entrega es individual.

El repositorio debe incluir:

- `analisis_desercion.py` con todos los TODO completados.
- `Data/processed/decisiones.csv` y la carpeta `Data/processed/graficos/`.
- Un `README.md` al final de este archivo, con una sección titulada **Mis decisiones y respuestas**. Debe incluir:
  0. El diccionario de datos: la tabla de las 23 columnas con tipo, descripción y rol, completada según el paso 1 de la guía.
  1. Tu diagnóstico de calidad: qué problemas encontraste y en qué columnas.
  2. Tus decisiones de limpieza, con su justificación.
  3. Las respuestas a las cinco preguntas, cada una con el número de estudiantes por grupo.
  4. Tu respuesta a la reflexión sobre asociación y causalidad.
  5. Tu respuesta a la reflexión sobre `motivo_retiro` y la predicción.
  6. Tu respuesta a la reflexión sobre el uso de variables sensibles.

El script debe ejecutarse sin errores desde cero. Cada decisión necesita una justificación, y cada conclusión debe apoyarse en un número del análisis.


# Mis decisiones y respuestas

**Estudiante:** Erica Avendaño A


## 0. Diccionario de datos

Aqui tenemos 23 columnas  con sus respectivos nombres: 
| Columna | Tipo | Descripción | Rol |
|---|---|---|---|
| id_estudiante | texto  | codigo unico que identifica cada estudiante  |  identificacion|
| programa | Categorica | Carrera o programa academica en la que esta inscrito el estudiante | Explicativa |
| facultad | Categorica | Facultad a la que pertenece el programa del estudiante  | Explicativa  |
| jornada |Categorica |Horario en que estudia: diurna, nocturna, o fin de semana  |Explicativa  |
| semestre |Numerica| Semestre que cursa actualmente el estudiante  | Explicativa |
| promedio_acumulado | Numerica | Promedio de notas de toda la carrera en escala de 0 a 5  | Explicativa  |
| creditos_aprobados | Numerica | Cantidad de creditos academicos que el estudiante ha aprobado | Explicativa  |
| materias_reprobadas | Numerica  | Cantidad de materias que el estudiante ha perdido  | Explicativa |
| asistencia_pct | Numerica  | Porcentaje de asistencia en clase  de 0 a 100  | Explicativa |
| sesiones_tutoria | Numericas | Cantidad de tutorias academicas en las que asistió el estudiante | Explicativa  |
| cambios_programa | Numerica  | numero de veces que el estudiante cambio de carrera  | Explicativa |
| estrato | Categorica |Extracto soscioeconomico de la vivienda del estudiante | Explicativa |
| beca | categórica | Indica si el estudiante recibe una beca (sí o no) | explicativa |
| trabaja | categórica | Indica si el estudiante trabaja mientras estudia (sí o no) | explicativa 
| horas_trabajo_semana | numérica | Horas que trabaja por semana. Llega como texto por los guiones | explicativa |
|distancia_km | numérica | Distancia en kilómetros entre la vivienda y la institución | explicativa |
| edad | Numerica  | Cuantos años tiene el estudiante | Explicativa |
| genero | Categorica  | Genero del estudiante Femenino o masculino | Explicativa  |
| ciudad_procedencia | Categorica  | Ciudad de origen del estudiante | Explicativa |
| tipo_colegio | Categorica | Tipo de colegio donde termino el bachiller  publico o privado  | Explicativa |
| fecha_matricula | Numerica  | Fecha la cual fué matriculado el estudiante  el dia, mes y año  | Explicativa |
| estado | categórica | Situación del estudiante: activo, graduado o desertor | resultado |
| motivo_retiro | Categorica  | Razon por la que el estudiante se retiró | Explicativa  |


## 1. Diagnóstico de calidad

El dataset original tiene 10.150 filas y 23 columnas. Encontré seis tipos de problema

**Nulos reales**

| Columna | Nulos | ¿Es error? |
|---|---|---|
| promedio_acumulado | 304 | Sí: todo estudiante tiene promedio |
| distancia_km | 199 | Sí |
| ciudad_procedencia | 103 | Sí |
| tipo_colegio | 152 | Sí |
| motivo_retiro | 6.877 | No: hay 3.273 valores llenos y 3.273 desertores. Solo aplica a quien deserta |

**Faltantes disfrazados:** __202_ guiones en asistencia_pct, __2822_ guiones en horas_trabajo_semana y _152__ valores 999 en distancia_km.

**Valores imposibles:** _12__ edades fuera de 15 a 60 (mínimo 12, máximo 150), _17__ promedios mayores a 5 (máximo 78) y _30__ registros con más de 100 horas de trabajo.

**Duplicados:** __150_ filas idénticas, incluido el id_estudiante.

**Errores tipográficos:** programa (Psicologia, Ingenieria de Sistemas sin tilde), jornada (diurna, nocturna, 'NOCTURNA ' con espacio), genero (M, F, femenino) y ciudad_procedencia (BOGOTÁ, Bogota, 'bogota ', medellin, 'Medellin ').

**Formatos inconsistentes:** __300_ asistencias con %, y __3052_ fechas en DD/MM/AAAA mezcladas con AAAA-MM-DD.

**El problema que más afecta:** los de formato y los imposibles. Si asistencia_pct sigue como texto, la pregunta 5 no se puede calcular. Si los promedios de 78 se quedan, el promedio sube de forma falsa (la media era 3,76 y la mediana 3,68: los valores extremos jalan la media hacia arriba) y cambia la respuesta de la pregunta 3.

La columna estado no tiene problemas: tres valores escritos igual y sin nulos.

## 2. Decisiones de limpieza

La tabla completa está en `Data/processed/decisiones.csv`. Las más importantes:

| Paso | Columna | Decisión | Por qué |
|---|---|---|---|
| 3 | asistencia_pct | Quitar %, guion a nulo, convertir a número | Como texto no permite promedios ni cuartiles |
| 3 | distancia_km | 999 a nulo | Es un código de "sin dato" que inflaría el promedio |
| 4 | programa, jornada, genero, ciudad | strip, lower y diccionario de variantes | La misma categoría se contaría como grupos distintos. M y F se traducen; "Otra ciudad" no se une con nada |
| 5 | fecha_matricula | Dos formatos unidos con fillna | Con un solo formato, parte de las fechas quedaría vacía |
| 6 | todas | Eliminar ___ duplicados | Tienen el mismo id: es el mismo estudiante copiado |
| 7 | promedio_acumulado | Eliminar filas nulas | Una nota no se inventa |
| 7 | ciudad, tipo_colegio | Reemplazar por "Sin dato" | Eliminar la fila perdería sus otros datos |
| 7 | motivo_retiro | No tocar | El nulo es esperado |
| 8 | promedio_acumulado | Eliminar los mayores a 5 | No sé con certeza en qué escala están; convertirlos sería suponer |
| 8 | edad | Fuera de 15 a 60 a la mediana | Es error de registro; la mediana no se afecta por extremos |
| 8 | horas_trabajo_semana | 0 si no trabaja; más de 100 a la mediana de quienes trabajan | La regla depende de otra columna |

El dataset limpio quedó con **_9687__ filas** y 25 columnas (las 23 originales más desertor y cuartil_asistencia).

## 3. Respuestas a las cinco preguntas

Tasa general de deserción en el dataset limpio: **__32.4_ %** (___ de _9687__ estudiantes).

1. **Programa con mayor deserción:** __Ingenieria Industrial_, con _40.2_ % de __1271_ estudiantes. Todos los programas tienen más de mil estudiantes, así que las tasas son confiables.
2. **Beca:** los becados desertan __21.9_ % (__2683_ estudiantes) y los no becados _36.4__ % (__7004_ estudiantes).
3. **Jornada con menor promedio:** _nocturna__, con promedio_3.46_ (__2666_ estudiantes).
4. **Materias reprobadas:** desertores _3.07__ (_3136__ estudiantes) frente a activos _0.62__ (__5692_ estudiantes). Excluí a los graduados porque no son ni desertores ni activos, y mezclarlos cambiaría la comparación.
5. **Asistencia:** la tasa pasa de __61.9_ % en Q1 (asistencia promedio __73.905_) a _0.94__ % en Q4 (asistencia promedio __98.660_). La deserción [aumenta / no aumenta] cuando baja la asistencia. 

## 4. Reflexión: asociación y causalidad

Que los becados deserten menos no prueba que la beca cause la permanencia. Puede haber otra explicación: las becas suelen darse a estudiantes con buen promedio, y esos estudiantes ya tenían menos riesgo de irse. También puede pesar el estrato o el apoyo familiar. Para saber si hay causa habría que comparar estudiantes parecidos en todo excepto en la beca, por ejemplo con un programa piloto que asigne becas y siga a los dos grupos en el tiempo.

## 5. Reflexión: motivo_retiro y la predicción

motivo_retiro no sirve para predecir, porque solo existe después de que el estudiante deserta. Si se usara, el modelo "acertaría" siempre, pero con información del futuro que nunca tendríamos a tiempo. El mismo cuidado aplica a cualquier dato registrado al final del proceso; por ejemplo, el estado mismo, o un promedio acumulado medido después del retiro.

## 6. Reflexión: uso de variables sensibles

Género, estrato y ciudad pueden reflejar desigualdades sociales. Si la institución los usa para decidir a quién apoyar, puede etiquetar a un grupo completo como "en riesgo" y dejar sin apoyo a estudiantes de otros grupos que sí lo necesitan. Es mejor basar las alertas en señales académicas que el estudiante puede cambiar, como la asistencia o las materias reprobadas, y usar las variables sensibles solo para revisar que los apoyos lleguen de forma justa.
