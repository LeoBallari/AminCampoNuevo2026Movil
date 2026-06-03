from flask import Flask, jsonify, request
from flask_cors import CORS
import pymssql

app = Flask(__name__)
CORS(app)

# === CONFIGURACIÓN DE SQL SERVER ===
# Separamos la IP y el Puerto para pymssql
SERVER = '190.103.87.151'        
PORT = 12433                     
DATABASE = 'Campo_LaReforma'  
USERNAME = 'lballari'     
PASSWORD = 'Clave.1369'  

def obtener_conexion():
    """Función auxiliar para conectar de forma limpia usando pymssql"""
    return pymssql.connect(
        server=SERVER,
        port=PORT,
        user=USERNAME,
        password=PASSWORD,
        database=DATABASE
    )

@app.route('/api/health')
def health():
    return jsonify({"status": "ok", "mensaje": "Servidor activo en Render"})

@app.route('/api/login', methods=['POST'])
def login():
    try:
        print("\n--- Intento de Login Recibido ---")
        data = request.get_json()
        user_input = data.get('usuario')
        pass_input = data.get('contraseña') 

        print(f"Usuario recibido: {user_input}")
        print("Intentando conectar a SQL Server con pymssql...")
        
        conn = obtener_conexion()
        cursor = conn.cursor()
        print("✅ Conexión a SQL Server exitosa")
        
        # Consulta segura parametrizada (en pymssql se usa %s en lugar de ?)
        query = "SELECT COUNT(*) FROM v2.Usuarios WHERE usuario = %s AND contraseña = %s"
        cursor.execute(query, (user_input, pass_input))
        exists = cursor.fetchone()[0]
        conn.close()

        print(f"Resultado de la consulta: {'Encontrado' if exists > 0 else 'No encontrado'}")

        if exists > 0:
            return jsonify({"success": True, "mensaje": "Login exitoso"})
        else:
            return jsonify({"success": False, "error": "Credenciales incorrectas"}), 401

    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/datos')
def get_datos():
    try:
        print(f"Intentando conectar a: {SERVER}:{PORT}")
        print(f"Base de datos: {DATABASE}")
        
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        cursor.execute("SELECT TOP 5 * FROM v2.Usuarios")
        
        # Obtener nombres de columnas
        columnas = [desc[0] for desc in cursor.description]
        
        # Convertir datos a JSON
        datos = []
        for fila in cursor.fetchall():
            fila_dict = {}
            for i, col in enumerate(columnas):
                valor = fila[i]
                if valor is None:
                    valor = ""
                elif hasattr(valor, 'strftime'):  # Para fechas
                    valor = valor.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    valor = str(valor)
                fila_dict[col] = valor
            datos.append(fila_dict)
        
        conn.close()
        
        return jsonify({
            "success": True,
            "cantidad": len(datos),
            "columnas": columnas,
            "datos": datos
        })
        
    except Exception as e:
        print(f"❌ ERROR EN DATOS: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 API Flask iniciada (Modo de prueba local)")
    print(f"📡 Conectando a SQL Server: {SERVER}:{PORT}")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)