from datetime import datetime, timedelta
import secrets
import string
from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

KEYS_BD = {}

def generar_key_aleatoria():
    caracteres = string.ascii_uppercase + string.digits
    bloque = ''.join(secrets.choice(caracteres) for _ in range(8))
    return f"KEY-{bloque}"

HTML_PANEL = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Generador de Licencias</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', sans-serif; }
        body { background-color: #080808; color: #ffffff; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .container { background: #111111; border: 1px solid #222222; border-radius: 12px; padding: 30px; width: 100%; max-width: 420px; box-shadow: 0 10px 30px rgba(181, 23, 158, 0.15); text-align: center; }
        h1 { font-size: 22px; margin-bottom: 8px; }
        p.sub { font-size: 13px; color: #888888; margin-bottom: 25px; }
        .grid-buttons { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 25px; }
        .btn-duracion { background: #181818; border: 1px solid #333333; color: #ffffff; padding: 12px; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s ease; }
        .btn-duracion:hover { background: #b5179e; border-color: #d946ef; transform: translateY(-2px); }
        .result-box { background: #0d0d0d; border: 1px dashed #b5179e; border-radius: 8px; padding: 15px; margin-top: 10px; display: none; }
        .key-text { font-family: monospace; font-size: 18px; color: #d946ef; font-weight: bold; letter-spacing: 1px; margin-bottom: 8px; }
        .info-text { font-size: 11px; color: #aaaaaa; }
        .btn-copiar { margin-top: 10px; background: transparent; border: 1px solid #d946ef; color: #d946ef; padding: 6px 12px; border-radius: 6px; font-size: 11px; cursor: pointer; }
        .btn-copiar:hover { background: #d946ef; color: #ffffff; }
    </style>
</head>
<body>
    <div class="container">
        <h1>KEY GENERATOR</h1>
        <p class="sub">Panel Administrador Local</p>
        <div class="grid-buttons">
            <button class="btn-duracion" onclick="generarKey(1)">1 Día</button>
            <button class="btn-duracion" onclick="generarKey(3)">3 Días</button>
            <button class="btn-duracion" onclick="generarKey(7)">7 Días</button>
            <button class="btn-duracion" onclick="generarKey(365)">365 Días</button>
        </div>
        <div id="resultBox" class="result-box">
            <div id="keyDisplay" class="key-text">KEY-XXXXXXXX</div>
            <div id="infoDisplay" class="info-text">Expira en: --</div>
            <button class="btn-copiar" onclick="copiarKey()">Copiar Key</button>
        </div>
    </div>
    <script>
        async function generarKey(dias) {
            try {
                const response = await fetch('/api/generar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ dias: dias })
                });
                const data = await response.json();
                if (data.success) {
                    document.getElementById('keyDisplay').innerText = data.key;
                    document.getElementById('infoDisplay').innerText = `Válida por ${data.dias} día(s) - Expira: ${data.expira}`;
                    document.getElementById('resultBox').style.display = 'block';
                }
            } catch (error) {
                alert('Error al conectar con el servidor.');
            }
        }
        function copiarKey() {
            const key = document.getElementById('keyDisplay').innerText;
            navigator.clipboard.writeText(key);
            alert('¡Key copiada al portapapeles!');
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PANEL)

@app.route('/api/generar', methods=['POST'])
def generar_key():
    data = request.get_json() or {}
    dias = int(data.get('dias', 1))
    
    nueva_key = generar_key_aleatoria()
    expiracion = datetime.now() + timedelta(days=dias)
    KEYS_BD[nueva_key] = expiracion

    return jsonify({
        "success": True,
        "key": nueva_key,
        "expira": expiracion.strftime("%Y-%m-%d %H:%M:%S"),
        "dias": dias
    })

@app.route('/api/validar', methods=['POST'])
def validar_key():
    data = request.get_json() or {}
    key = data.get('key', '').strip()

    if key in KEYS_BD:
        expiracion = KEYS_BD[key]
        if datetime.now() < expiracion:
            return jsonify({
                "valida": True, 
                "expira": expiracion.strftime("%Y-%m-%d %H:%M:%S")
            })
        else:
            return jsonify({"valida": False, "mensaje": "Key expirada"})
    return jsonify({"valida": False, "mensaje": "Key inválida"})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)