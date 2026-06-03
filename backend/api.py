from flask import Flask, jsonify, request
from flask_cors import CORS
import pymssql

app = Flask(__name__)
CORS(app)

# Configuración de tu SQL Server
SERVER = '190.103.87.151'        
PORT = 12433                     
DATABASE = 'Campo_LaReforma'  
USERNAME = 'lballari'     
PASSWORD = 'Clave.1369'  

def obtener_conexion():
    return pymssql.connect(
        server=SERVER,
        port=PORT,
        user=USERNAME,
        password=PASSWORD,
        database=DATABASE,
        login_timeout=10,
        timeout=10,
        tds_version='7.0'  # Cambiamos a 7.0 para igualar la compatibilidad de jTDS
    )
    
@app.route('/api/health')
def health():
    return jsonify({"status": "ok", "mensaje": "Servidor activo en Render"})

@app.route('/api/login', methods=['POST'])
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)