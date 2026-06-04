from flask import Blueprint, request, jsonify
from database import obtener_conexion

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user_input = data.get('usuario')
        pass_input = data.get('contraseña') 
        
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        # Consulta para verificar el usuario
        query = "SELECT COUNT(*) FROM v2.Usuarios WHERE usuario = %s AND contraseña = %s"
        cursor.execute(query, (user_input, pass_input))
        exists = cursor.fetchone()[0]
        conn.close()

        if exists > 0:
            return jsonify({"success": True, "mensaje": "Login exitoso"})
        else:
            return jsonify({"success": False, "error": "Credenciales incorrectas"}), 401

    except Exception as e:
        print("======== ERROR DETECTADO ========")
        print(str(e))
        print("=================================")
        return jsonify({"success": False, "error": str(e)}), 500