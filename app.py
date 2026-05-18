from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

INTERPRETACIONES = {
    "NO ENFERMO": "Sin crisis drepanocítica activa. Control ambulatorio de rutina.",
    "ENFERMEDAD LEVE": "Crisis leve. Manejo ambulatorio con analgesia e hidratación oral.",
    "ENFERMEDAD AGUDA": "Crisis moderada. Observación hospitalaria, analgesia IV e hidratación.",
    "ENFERMEDAD CRÓNICA": "Crisis grave / Síndrome Torácico Agudo. Hospitalización urgente.",
}


def predecir_crisis(spo2: float, dolor: int, hemoglobina: float,
                    fiebre: float, frecuencia_respiratoria: int,
                    crisis_previas_6m: int = 0) -> str:
    """
    Función simulada de predicción de crisis drepanocítica.
    No corresponde a un modelo real ni debe usarse para decisiones médicas.

    Parámetros:
    - spo2: saturación de oxígeno en %.
    - dolor: escala de 0 a 10.
    - hemoglobina: g/dL.
    - fiebre: temperatura en grados Celsius.
    - frecuencia_respiratoria: respiraciones por minuto.
    - crisis_previas_6m: número de crisis en los últimos 6 meses.

    Retorna:
    - NO ENFERMO              → sin crisis activa
    - ENFERMEDAD LEVE         → crisis leve, manejo ambulatorio
    - ENFERMEDAD AGUDA        → crisis moderada, observación hospitalaria
    - ENFERMEDAD CRÓNICA      → crisis grave / síndrome torácico agudo
    """
    # Crisis grave o síndrome torácico agudo
    if spo2 < 90 or frecuencia_respiratoria > 30 or hemoglobina < 5:
        return "ENFERMEDAD CRÓNICA"
    # Crisis moderada
    if spo2 < 94 or dolor >= 8 or hemoglobina < 7:
        return "ENFERMEDAD AGUDA"
    # Crisis leve
    if dolor >= 4 or fiebre >= 38.5 or crisis_previas_6m >= 3:
        return "ENFERMEDAD LEVE"
    return "NO ENFERMO"


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/predecir", methods=["POST"])
def predecir():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

        spo2 = float(data.get("spo2"))
        dolor = int(data.get("dolor"))
        hemoglobina = float(data.get("hemoglobina"))
        fiebre = float(data.get("fiebre"))
        frecuencia_respiratoria = int(data.get("frecuencia_respiratoria"))
        crisis_previas_6m = int(data.get("crisis_previas_6m", 0))

        resultado = predecir_crisis(spo2, dolor, hemoglobina, fiebre,
                                    frecuencia_respiratoria, crisis_previas_6m)
        interpretacion = INTERPRETACIONES[resultado]

        if request.is_json:
            return jsonify({
                "entrada": {
                    "spo2": spo2,
                    "dolor": dolor,
                    "hemoglobina": hemoglobina,
                    "fiebre": fiebre,
                    "frecuencia_respiratoria": frecuencia_respiratoria,
                    "crisis_previas_6m": crisis_previas_6m,
                },
                "resultado": resultado,
                "interpretacion_clinica": interpretacion,
            })

        return render_template("index.html", resultado=resultado,
                               interpretacion=interpretacion)

    except Exception as error:
        mensaje = "Datos inválidos. Revise todos los campos obligatorios."
        if request.is_json:
            return jsonify({"error": mensaje, "detalle": str(error)}), 400
        return render_template("index.html", error=mensaje), 400


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
