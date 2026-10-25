from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Habilita CORS para permitir las peticiones desde tu app de escritorio

# --- TU BASE DE DATOS DE KEYS ---
# Aquí puedes agregar todas las keys que quieras y su fecha de expiración
KEYS_VALIDAS = {
    "KEY-CYQAAFPQ": "2026-12-31 23:59:59",
    "OTRA-KEY-123": "2026-06-30 12:00:00"
}

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
        
        # Verificamos si la key existe en nuestro diccionario
        if key_ingresada in KEYS_VALIDAS:
            return jsonify({
                "valida": True,
                "expira": KEYS_VALIDAS[key_ingresada]
            }), 200
        else:
            return jsonify({
                "valida": False, 
                "mensaje": "Key inválida o expirada"
            }), 200  # Usamos 200 para que la app procese el mensaje JSON correctamente

    except Exception as e:
        print(f"Error en el servidor: {e}")
        return jsonify({
            "valida": False, 
            "mensaje": "Error interno en el servidor"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
