from flask import Flask, jsonify
from flask_cors import CORS
# Importamos los planos de las rutas que armamos
from routes.auth_routes import auth_bp
from routes.despachos_routes import despachos_bp

app = Flask(__name__)
CORS(app)

# === REGISTRO DE MÓDULOS (BLUEPRINTS) ===
app.register_blueprint(auth_bp)
app.register_blueprint(despachos_bp)

@app.route('/api/health', methods=['GET'])
def health():
    """Ruta de control para saber si Render sigue vivo"""
    return jsonify({"status": "ok", "mensaje": "Servidor activo en Render"})

if __name__ == '__main__':
    # Para probar en tu PC localmente
    app.run(host='0.0.0.0', port=5000)