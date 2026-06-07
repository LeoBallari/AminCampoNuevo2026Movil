from flask import Flask, jsonify
from flask_cors import CORS
# Importamos los planos de las rutas que armamos
from routes.auth_routes import auth_bp
from routes.despachos_routes import despachos_bp
from routes.cosecha_routes import cosecha_bp
from routes.siembra_routes import siembra_bp
from routes.lotes_routes import lotes_bp
from routes.estadisticas_routes import estadisticas_bp

app = Flask(__name__)
CORS(app)

# === REGISTRO DE MÓDULOS (BLUEPRINTS) ===
app.register_blueprint(auth_bp)
app.register_blueprint(despachos_bp)
app.register_blueprint(cosecha_bp)
app.register_blueprint(siembra_bp)
app.register_blueprint(lotes_bp)
app.register_blueprint(estadisticas_bp)  # Agrega el blueprint de estadísticas

@app.route('/api/health', methods=['GET'])
def health():
    """Ruta de control para saber si Render sigue vivo"""
    return jsonify({"status": "ok", "mensaje": "Servidor activo en Render"})

if __name__ == '__main__':
    # Para probar en tu PC localmente
    app.run(host='0.0.0.0', port=5000)