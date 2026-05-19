# Servicio Docker para evaluacion de crisis drepanocitica

## Problema y proposito

Este proyecto corresponde a una actividad academica de MLOps. La aplicacion simula la evaluacion de severidad de una crisis en pacientes con drepanocitosis (anemia falciforme) y expone resultados por API y formulario web.

No es un modelo clinico real ni debe usarse para decisiones medicas.

## Categorias de prediccion

El sistema retorna 5 categorias:

- NO ENFERMO
- ENFERMEDAD LEVE
- ENFERMEDAD AGUDA
- ENFERMEDAD CRONICA
- ENFERMEDAD TERMINAL

## Estructura del repositorio

```text
camilo-mlops-U2/
|- app.py
|- Dockerfile
|- requirements.txt
|- README.md
|- templates/
|  |- index.html
|- tests/
|  |- test_app.py
`- .github/
   `- workflows/
      `- ci-cd.yml
```

## Requerimientos implementados en Unidad 2

### 1) Nueva categoria: ENFERMEDAD TERMINAL

Se agrego una condicion de mayor severidad para simular estado critico.

### 2) Nueva funcionalidad: reporte de estadisticas

Se agrego persistencia en archivo JSON para registrar cada prediccion y exponer:

- Numero total de predicciones por categoria.
- Ultimas 5 predicciones realizadas.
- Fecha de la ultima prediccion.

Endpoint:

```text
GET /estadisticas
```

Archivo de persistencia por defecto:

```text
data/estadisticas_predicciones.json
```

## Uso local

### Ejecutar con Python

```bash
pip install -r requirements.txt
python app.py
```

Abrir en navegador:

```text
http://localhost:5000
```

### Ejecutar con Docker

```bash
docker build -t mlops-enfermedades .
docker run -p 5000:5000 mlops-enfermedades
```

## API

### Prediccion

```text
POST /predecir
```

Ejemplo:

```bash
curl -X POST http://localhost:5000/predecir \
  -H "Content-Type: application/json" \
  -d '{"spo2":84,"dolor":9,"hemoglobina":3.8,"fiebre":39.1,"frecuencia_respiratoria":42,"crisis_previas_6m":4}'
```

### Estadisticas

```text
GET /estadisticas
```

Ejemplo:

```bash
curl http://localhost:5000/estadisticas
```

## CI/CD

El workflow de GitHub Actions en .github/workflows/ci-cd.yml ejecuta:

- En pull_request hacia main: comentario de inicio, pruebas unitarias y comentario de exito.
- En push a main: pruebas unitarias, build de imagen Docker y publicacion en GHCR.

## Nota

Este repositorio es academico y esta orientado a buenas practicas de versionamiento, pruebas y despliegue en MLOps.
