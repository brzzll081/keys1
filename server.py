from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import random
import string
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

ARCHIVO_KEYS = "keys.json"

# Cargar o inicializar la base de datos de keys
def cargar_keys():
    if os.path.exists(ARCHIVO_KEYS):
        try:
            with open(ARCHIVO_KEYS, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def guardar_keys(keys_dict):
    with open(ARCHIVO_KEYS, "w", encoding="utf-8") as f:
        json.dump(keys_dict, f, indent=4)

KEYS_VALIDAS = cargar_keys()

# --- PANEL WEB INTERACTIVO PARA GENERAR KEYS ---
@app.route('/', methods=['GET'])
def home():
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Panel Generador de Keys</title>
        <style>
            body {
                background-color: #0b0b0b;
                color: #ffffff;
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .card {
                background-color: #111111;
                border: 1px solid #222222;
                padding: 30px;
                border-radius: 12px;
                text-align: center;
                width: 360px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.7);
            }
            h1 {
                color: #b026ff;
                font-size: 18px;
                margin-bottom: 20px;
            }
            .btn-container {
                display: flex;
                flex-direction: column;
                gap: 10px;
                margin-bottom: 20px;
            }
            button {
                background-color: #b026ff;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                cursor: pointer;
                transition: background 0.2s;
            }
            button:hover {
                background-color: #9a1fe0;
            }
            #resultado {
                background: #181818;
                padding: 12px;
                border-radius: 6px;
                font-family: monospace;
                font-size: 14px;
                color: #00ff66;
                word-break: break-all;
                display: none;
                border: 1px solid #333;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>GENERADOR DE KEYS</h1>
            <div class="btn-container">
                <button onclick="generarKey(1)">Generar Key de 1 Día</button>
                <button onclick="generarKey(3)">Generar Key de 3 Días</button>
                <button onclick="generarKey(7)">Generar Key de 7 Días</button>
                <button onclick="generarKey(365)">Generar Key de 365 Días</button>
            </div>
            <div id="resultado"></div>
        </div>

        <script>
            function generarKey(dias) {
                fetch('/api/generar/' + dias, { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        const resDiv = document.getElementById('resultado');
                        resDiv.style.display = 'block';
                        if(data.success) {
                            resDiv.innerHTML = "<b>Key (" + dias + "d):</b><br>" + data.key + "<br><small style='color:#aaa;'>Expira: " + data.expira + "</small>";
                        } else {
                            resDiv.innerHTML = "Error al generar";
                        }
                    })
                    .catch(err => {
                        console.error(err);
                        alert("Error de conexión");
                    });
            }
        </script>
    </body>
    </html>
    """
    return html_content, 200

# --- RUTA PARA CREAR KEYS AL HACER CLIC EN LA WEB ---
@app.route('/api/generar/<int:dias>', methods=['POST'])
def generar_key_endpoint(dias):
    global KEYS_VALIDAS
    KEYS_VALIDAS = cargar_keys()
    
    # Crear código aleatorio único
    prefijo = f"{dias}D"
    caracteres = string.ascii_uppercase + string.digits
    sufijo = ''.join(random.choices(caracteres, k=8))
    nueva_key = f"{prefijo}-{sufijo}"
    
    while nueva_key in KEYS_VALIDAS:
        sufijo = ''.join(random.choices(caracteres, k=8))
        nueva_key = f"{prefijo}-{sufijo}"
        
    # Calcular fecha de expiración
    fecha_exp = datetime.now() + timedelta(days=dias)
    fecha_str = fecha_exp.strftime("%Y-%m-%d %H:%M:%S")
    
    # Guardar en el diccionario y archivo
    KEYS_VALIDAS[nueva_key] = fecha_str
    guardar_keys(KEYS_VALIDAS)
    
    return jsonify({
        "success": True,
        "key": nueva_key,
        "expira": fecha_str
    }), 200

# --- RUTA DE VALIDACIÓN PARA TU APP DE ESCRITORIO ---
@app.route('/api/validar', methods=['POST'])
def validar():
    try:
        datos = request.get_json()
        
        if not datos or "key" not in datos:
            return jsonify({
                "valida": False, 
                "mensaje": "No se proporcionó ninguna key"
            }), 400
            
        key_ingresada = datos.get("key").strip()
        
        global KEYS_VALIDAS
        KEYS_VALIDAS = cargar_keys()
        
        if key_ingresada in KEYS_VALIDAS:
            return jsonify({
                "valida": True,
                "expira": KEYS_VALIDAS[key_ingresada]
            }), 200
        else:
            return jsonify({
                "valida": False, 
                "mensaje": "Key inválida o expirada"
            }), 200

    except Exception as e:
        print(f"Error en el servidor: {e}")
        return jsonify({
            "valida": False, 
            "mensaje": "Error interno en el servidor"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
