import json
import os
import sys

# Ensure repository root is on sys.path so CI can import app.py
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import app as app_module


def _entrada_base():
    return {
        "spo2": 98,
        "dolor": 1,
        "hemoglobina": 12.0,
        "fiebre": 36.8,
        "frecuencia_respiratoria": 16,
        "crisis_previas_6m": 0,
    }


def test_prediccion_terminal():
    resultado = app_module.predecir_crisis(
        spo2=84,
        dolor=9,
        hemoglobina=3.8,
        fiebre=39.0,
        frecuencia_respiratoria=42,
        crisis_previas_6m=4,
    )
    assert resultado == "ENFERMEDAD TERMINAL"


def test_estadisticas_iniciales_vacias(tmp_path, monkeypatch):
    stats_file = tmp_path / "estadisticas.json"
    monkeypatch.setattr(app_module, "STATS_FILE", str(stats_file))

    client = app_module.app.test_client()
    response = client.get("/estadisticas")

    assert response.status_code == 200
    data = response.get_json()
    assert data["fecha_ultima_prediccion"] is None
    assert data["ultimas_5_predicciones"] == []
    assert all(valor == 0 for valor in data["total_por_categoria"].values())


def test_estadisticas_registran_ultima_prediccion(tmp_path, monkeypatch):
    stats_file = tmp_path / "estadisticas.json"
    monkeypatch.setattr(app_module, "STATS_FILE", str(stats_file))

    client = app_module.app.test_client()
    payload = _entrada_base()

    response_pred = client.post("/predecir", data=json.dumps(payload), content_type="application/json")
    assert response_pred.status_code == 200

    response_stats = client.get("/estadisticas")
    assert response_stats.status_code == 200
    stats = response_stats.get_json()

    assert stats["fecha_ultima_prediccion"] is not None
    assert len(stats["ultimas_5_predicciones"]) == 1
    assert stats["ultimas_5_predicciones"][0]["resultado"] == "NO ENFERMO"
    assert stats["total_por_categoria"]["NO ENFERMO"] == 1
