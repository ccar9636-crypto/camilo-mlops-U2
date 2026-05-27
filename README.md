# Descripcion de un Pipeline de MLOps para evaluacion de crisis drepanocitica

## Proposito

Este documento presenta una propuesta reestructurada del pipeline end-to-end para la evaluación de crisis drepanocítica. El objetivo es presentar una solución de MLOps para predecir, a partir de síntomas y antecedentes clínicos, el riesgo y el nivel de severidad de una crisis.

El documento está dirigido a un público clínico y de ingeniería. Incluye supuestos, decisiones de arquitectura, tecnologías sugeridas, estrategias de monitoreo y retraining, y un changelog que explica las diferencias frente a la propuesta original.

## Contexto del problema

El reto parte de una realidad comun en salud: existen pocos datos para algunas enfermedades huérfanas y muchos datos para enfermedades frecuentes. En esta propuesta el problema de referencia es la evaluacion de crisis drepanocitica, lo cual exige un pipeline que soporte:

- datos historicos escasos o desbalanceados,
- explicabilidad para el personal medico,
- versionamiento y trazabilidad de datos y modelos,
- despliegue local o en nube,
- monitoreo de deriva y rendimiento con realimentacion continua.

La salida esperada no es solo un modelo, sino un sistema mantenible que pueda evolucionar sin perder control sobre calidad, seguridad y reproducibilidad.

## Alcance de la propuesta

La solucion se plantea como un pipeline modular que cubre desde la definicion del problema hasta la operacion en produccion. El medico puede usarla de dos formas:

- en su computador local si el modelo y los recursos son livianos,
- mediante peticiones a un servicio alojado en la nube o en un servidor institucional.

## Supuestos

Para que la propuesta sea ejecutable, se asumen las siguientes condiciones:

- Los datos de entrada corresponden a sintomas clinicos estructurados y medibles, como temperatura, saturacion de oxigeno, frecuencia respiratoria, dolor y antecedentes recientes.
- Existe una variable objetivo definida por expertos que representa la presencia o severidad de la enfermedad.
- El historico de datos puede contener clases desbalanceadas, especialmente si se trata de enfermedades huérfanas.
- El personal medico necesita respuestas rapidas y una explicacion basica de la prediccion.
- Se permite almacenar trazabilidad minima de predicciones para auditoria y monitoreo, cumpliendo politicas de privacidad y acceso.
- El ciclo de retraining se ejecuta de forma controlada, no automatica sin aprobacion, al menos en la primera version.

## Arquitectura general

```mermaid
flowchart LR
   A[Fuentes de datos clinicos] --> B[Ingesta y validacion]
   B --> C[Versionamiento de datos]
   C --> D[EDA y preparacion de features]
   D --> E[Entrenamiento y tuning]
   E --> F[Tracking de experimentos]
   F --> G[Evaluacion y aprobacion]
   G --> H[Registro de modelo]
   H --> I[Empaquetado y despliegue]
   I --> J[Inferencia local o via API]
   J --> K[Monitoreo y logging]
   K --> L[Deteccion de deriva y retraining]
   L --> D
```

## Pipeline propuesto

### 1. Definicion del problema y criterios de exito

Antes de modelar, el equipo debe fijar claramente:

- la variable objetivo,
- el tipo de problema: clasificacion binaria o multiclase,
- el costo de los errores,
- la latencia maxima aceptable,
- el nivel minimo de interpretabilidad requerido,
- las metricas de exito tecnica y clinica.

**Tecnologias sugeridas:** Jira o Notion para requerimientos, reuniones con expertos, y un documento de definicion del problema versionado en Git.

**Justificacion:** en salud no basta con maximizar accuracy; un falso negativo puede ser mucho mas costoso que un falso positivo. Esta etapa evita que el pipeline se construya sobre una definicion ambigua.

### 2. Ingesta y gobierno de datos

Los datos deben llegar desde historia clinica, formularios, laboratorios o una base transaccional. En esta fase se valida estructura, rangos posibles y completitud.

**Tecnologias sugeridas:**

- Airflow para orquestar ingestas programadas,
- SQL o APIs REST para obtener datos,
- Great Expectations o Pandera para validacion de calidad,
- almacenamiento en un data lake o en archivos versionados.

**Justificacion:** la validacion automatica reduce el riesgo de entrenar con datos corruptos o incompletos. Airflow permite dejar trazado cada paso y reintentar si una fuente falla.

### 3. Versionamiento y trazabilidad de datos

Toda version del dataset debe quedar identificada junto con su esquema, fecha y reglas de transformacion.

**Tecnologias sugeridas:** DVC, Git LFS o Delta Lake segun la escala.

**Justificacion:** en un entorno medico se necesita reproducir exactamente por que un modelo fue entrenado de cierta manera. Sin versionamiento, no hay auditoria real.

### 4. Exploracion, limpieza y analisis de sesgos

Esta etapa busca entender distribuciones, faltantes, outliers, clases desbalanceadas y posibles sesgos por subpoblacion.

Se debe documentar, como minimo:

- distribucion de cada sintoma,
- correlaciones relevantes,
- tratamiento de valores faltantes,
- balance de clases,
- posibles variables redundantes,
- riesgo de leakage.

**Tecnologias sugeridas:** Python, pandas, seaborn, matplotlib, y reportes automaticos como Sweetviz o ydata-profiling.

**Justificacion:** en este problema la calidad de los datos es tan importante como el algoritmo. Un analisis temprano evita seleccionar features poco utiles o peligrosas.

### 5. Ingenieria de features

Se proponen transformaciones simples y explicables antes de probar modelos mas complejos:

- escalado de variables numericas si el modelo lo requiere,
- codificacion de categoricas si aparecen,
- construccion de features clinicas agregadas,
- indicadores de severidad basados en umbrales medicos,
- tratamiento especial del desbalance.

**Tecnologias sugeridas:** scikit-learn, imbalanced-learn y pipelines reproducibles.

**Justificacion:** para un caso medico, features transparentes facilitan interpretabilidad y revision por expertos. Si se agregan variables derivadas, deben poder justificarse clinicamente.

### 6. Entrenamiento y seleccion de modelos

Se recomienda empezar con modelos interpretables y luego comparar contra opciones mas flexibles:

- Regresion Logistica,
- Random Forest,
- XGBoost o LightGBM,
- CatBoost si hay variables categoricas relevantes.

**Tecnologias sugeridas:** scikit-learn, XGBoost, LightGBM, Optuna para busqueda de hiperparametros.

**Justificacion:** un baseline interpretable sirve como referencia. Los modelos de ensamble suelen capturar mejor interacciones no lineales, algo util en sintomas medicos.

### 7. Tracking de experimentos

Cada corrida debe registrar parametros, metricas, artefactos y version de datos.

**Tecnologias sugeridas:** MLflow o Weights & Biases.

**Justificacion:** permite comparar versiones, reproducir entrenamientos y elegir el mejor modelo sin depender de notas manuales o archivos sueltos.

### 8. Evaluacion tecnica y clinica

La evaluacion debe incluir metricas clasicas y metricas orientadas al negocio o al riesgo clinico:

- precision, recall y F1,
- AUC-ROC y AUC-PR,
- matriz de confusion,
- recall de la clase critica,
- calibration curve si aplica,
- analisis de explicabilidad con SHAP o LIME.

**Justificacion:** en salud el recall de las clases de mayor riesgo suele ser prioritario. La calibracion y la explicabilidad ayudan a que el medico confie en la salida del sistema.

### 9. Registro y aprobacion del modelo

El mejor candidato no debe ir directo a produccion. Primero pasa por un registro con aprobacion.

**Tecnologias sugeridas:** MLflow Model Registry, o un registro equivalente en el cloud provider.

**Justificacion:** el registro formal separa entrenamiento de despliegue y habilita control de version, estado y aprobacion manual.

### 10. Empaquetado y despliegue

El modelo aprobado se empaqueta como servicio de inferencia.

**Opciones de despliegue:**

- local, en el computador del medico, con Docker o ejecucion directa en Python si el consumo es bajo,
- centralizado, como API en nube o servidor interno.

**Tecnologias sugeridas:** FastAPI o Flask, Docker, Kubernetes si se requiere escalado, y un reverse proxy como Nginx.

**Justificacion:** Docker asegura portabilidad. La API permite desacoplar la inferencia de la interfaz y facilita integrar la solucion en otros sistemas clinicos.

### 11. Monitoreo en produccion

La operacion no termina con el despliegue. Debe monitorearse el comportamiento del modelo y de los datos.

Se propone monitorear:

- latencia de respuesta,
- tasa de error,
- distribucion de entradas,
- deriva de datos,
- deriva de concepto cuando haya etiquetas reales,
- cambios en la distribucion de predicciones,
- volumen de uso por medico o por unidad de tiempo.

**Tecnologias sugeridas:** Prometheus, Grafana, Evidently AI, logs centralizados en ELK o un stack equivalente.

**Justificacion:** el entorno medico puede cambiar rapidamente. Si cambia la poblacion o los rangos de sintomas, el modelo puede degradarse sin que el equipo lo note.

### 12. Feedback y retraining

Cuando el monitoreo detecte degradacion, se activa un proceso de reentrenamiento.

**Tecnologias sugeridas:** Airflow para orquestar retraining, MLflow para comparar con modelos previos, y aprobacion humana antes de liberar una nueva version.

**Justificacion:** esto cierra el ciclo de MLOps. El sistema aprende de nuevo datos, pero siempre bajo control y con trazabilidad.

## Tecnologias recomendadas por etapa

| Etapa | Tecnologias | Motivo principal |
|---|---|---|
| Definicion del problema | Git, documentos de requerimientos | Mantener criterios de exito trazables |
| Ingesta | Airflow, APIs, SQL | Automatizar flujos y reintentos |
| Validacion de datos | Great Expectations, Pandera | Detectar errores antes del entrenamiento |
| Versionamiento | DVC, Git LFS, Delta Lake | Reproducibilidad y auditoria |
| Analisis | pandas, seaborn, matplotlib | Entender sesgos y calidad |
| Entrenamiento | scikit-learn, XGBoost, LightGBM, Optuna | Comparar modelos y ajustar hiperparametros |
| Tracking | MLflow, W&B | Centralizar metricas y artefactos |
| Registro | MLflow Registry | Aprobar y versionar modelos |
| Despliegue | Flask o FastAPI, Docker, Kubernetes | Portabilidad y escalabilidad |
| Monitoreo | Prometheus, Grafana, Evidently AI | Vigilar salud del sistema |

## Como se resuelve la restriccion de uso local o en nube

La solucion se disena para dos modos de consumo:

### Modo local

Si el modelo es liviano y la frecuencia de uso es baja, el medico puede correr una instancia local en su equipo.

Ventajas:

- menor dependencia de conectividad,
- respuesta rapida en contextos offline,
- facil adopcion en entornos con infraestructura limitada.

Limitaciones:

- actualizaciones mas manuales,
- menor capacidad de centralizar trazabilidad,
- riesgo de versiones divergentes si no se controla el despliegue.

### Modo nube o servidor

Si se necesita disponibilidad compartida, el modelo se expone como API.

Ventajas:

- una sola version operativa,
- monitoreo centralizado,
- actualizaciones controladas,
- integracion con otros sistemas.

Limitaciones:

- dependencia de red,
- requiere autenticacion y control de acceso,
- costos de infraestructura.

## Criterios de calidad y riesgo

La propuesta debe contemplar explicitamente los siguientes riesgos:

- desbalance extremo entre clases,
- falsos negativos clinicamente criticos,
- fuga de informacion entre entrenamiento y prueba,
- cambios de distribucion por contexto hospitalario,
- explicabilidad insuficiente para uso medico,
- incumplimiento de privacidad si se registran datos sensibles sin control.

Para mitigar estos riesgos se recomienda:

- muestreo estratificado,
- metricas enfocadas en recall de la clase critica,
- validacion estricta de features,
- aprobacion manual de modelos,
- politicas claras de logging y anonimizacion.

## Relacion con el repositorio actual

El repositorio puede seguir manteniendo la aplicacion demo de inferencia como una pieza de referencia para la etapa de despliegue. Sin embargo, esta entrega documenta el pipeline completo que deberia existir alrededor de esa aplicacion para que la solucion sea realmente operable como producto ML.

## CHANGELOG frente a la propuesta de la semana 1

| Aspecto | Semana 1 | Propuesta actual |
|---|---|---|
| Alcance | Descripcion general del problema y una idea inicial de modelado | Pipeline end-to-end con operacion, monitoreo y retraining |
| Datos | Se mencionaban sintomas y prediccion | Se agregan supuestos, versionamiento, validacion y gobierno de datos |
| Modelado | Se proponia construir un clasificador | Se comparan modelos, se incluyen metricas, tuning y explicabilidad |
| Despliegue | No se detallaba a profundidad | Se definen opciones local y nube, con Docker y API |
| Operacion | Practicamente ausente | Se agregan monitoreo, logging, deriva y ciclo de retraining |
| Trazabilidad | Limitada o inexistente | Se incorpora MLflow, versionado de datos y registro de modelos |
| Documentacion | Basica | Se documentan supuestos, riesgos y decisiones tecnicas |

## Estructura sugerida para implementar la propuesta

```text
camilo-mlops-U2/
|- app.py
|- Dockerfile
|- requirements.txt
|- README.md
|- data/
|  `- estadisticas_predicciones.json
|- templates/
|  `- index.html
`- tests/
  `- test_app.py
```

## Conclusion

La reestructuracion convierte una idea inicial de clasificacion medica en una propuesta MLOps completa, justificable y operable. El foco no es solo entrenar un modelo, sino diseñar un sistema reproducible, auditable y preparado para evolucionar con nuevos datos y nuevas condiciones clinicas.
