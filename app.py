# app.py
import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from PIL import Image
import io
import google.generativeai as genai

# carga .env en desarrollo
load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")

# Configura tu API Key (asegúrate de tener GEMINI_API_KEY en .env o en variables de entorno)
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("Pon tu GEMINI_API_KEY en .env o en las variables de entorno.")
genai.configure(api_key=API_KEY)

# Ajusta el nombre del modelo según tu suscripción (esto puede variar)
MODEL_NAME = "gemini-2.5-pro"  # si tu cuenta usa otro nombre, cámbialo

# Contexto fijo que aplicará a todas las consultas
CONTEXT = """
Eres un asistente experto en programación Java.
Tu tarea es guiar paso a paso el proceso para resolver ejercicios,
pero NUNCA des la respuesta final ni el código completo.
Solo explica la lógica, el razonamiento y los pasos necesarios,
como un profesor que guía al estudiante.
Responde de forma clara, concisa y en lenguaje accesible.
"""

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/preguntar", methods=["POST"])
def preguntar():
    # Recibimos texto y/o imagen
    pregunta = request.form.get("pregunta", "").strip()
    imagen_file = request.files.get("imagen")

    # Armamos las "partes" del prompt para enviar al modelo
    partes = []

    # Parte de texto con contexto + pregunta
    texto_prompt = f"{CONTEXT}\n\nEl estudiante pregunta: {pregunta}\n\nPor favor responde siguiendo las reglas anteriores."
    partes.append({"text": texto_prompt})

    # Si hay imagen, leemos bytes y añadimos como parte binaria
    if imagen_file:
        # Leemos bytes (no guardamos a disco)
        imagen_bytes = imagen_file.read()
        # Intentamos detectar mime
        mime_type = imagen_file.mimetype or "image/jpeg"
        # Añadimos la parte de imagen (esto asume que la librería acepta partes con mime + data)
        partes.append({"mime_type": mime_type, "data": imagen_bytes})

    # Llamada a la API de Gemini (usa GenerativeModel)
    model = genai.GenerativeModel(MODEL_NAME)

    # Intentamos generar contenido. La forma exacta de la llamada puede variar según versión
    try:
        # generate_content acepta partes (texto + imágenes) en muchas versiones
        result = model.generate_content(parts)
        # 'result' debería tener texto en result.text o result.output_text. Intentamos varias opciones:
        respuesta_text = getattr(result, "text", None) or getattr(result, "output_text", None) or str(result)
    except Exception as e:
        # Si algo sale mal, devolvemos error para depurar
        return jsonify({"error": "Error al llamar a la API de Gemini", "detail": str(e)}), 500

    return jsonify({"respuesta": respuesta_text})

if __name__ == "__main__":
    # puerto 8080 es cómodo para despliegues (replit, render, etc.)
    app.run(host="0.0.0.0", port=8080, debug=True)