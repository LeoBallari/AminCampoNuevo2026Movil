from flask import Flask, jsonify, request
from flask_cors import CORS
import pyodbc

app = Flask(__name__)
CORS(app)

# === CONFIGURACIÓN DE SQL SERVER - CAMBIA ESTOS VALORES ===
SERVER = '190.103.87.151,12433'        # Cambia por IP o nombre de tu servidor
DATABASE = 'Campo_LaReforma'  # Cambia por el nombre real de tu BD
USERNAME = 'lballari'     # Cambia por tu usuario
PASSWORD = 'Clave.1369'  # Cambia por tu contraseña

# Usar el driver ODBC 18 (tienes este instalado)
DRIVER = '{ODBC Driver 18 for SQL Server}'

@app.route('/api/health')
def health():
    return jsonify({"status": "ok", "mensaje": "Servidor activo"})

@app.route('/api/login', methods=['POST'])
def login():
    try:
        print("\n--- Intento de Login Recibido ---")
        data = request.get_json()
        user_input = data.get('usuario')
        # Corregimos 'contraseña' por 'password' para que coincida con el frontend
        pass_input = data.get('contraseña') 

        print(f"Usuario recibido: {user_input}")
        
        print("Intentando conectar a SQL Server...")
        conn_str = (
            f'DRIVER={DRIVER};'
            f'SERVER={SERVER};'
            f'DATABASE={DATABASE};'
            f'UID={USERNAME};'
            f'PWD={PASSWORD};'
            f'TrustServerCertificate=yes;'
            f'Encrypt=yes'
        )
        
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        print("✅ Conexión a SQL Server exitosa")
        
        # Usamos nombres de columnas según tu tabla v2.Usuarios
        query = "SELECT COUNT(*) FROM v2.Usuarios WHERE usuario = ? AND contraseña = ?"
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
        # Construir cadena de conexión
        conn_str = (
            f'DRIVER={DRIVER};'
            f'SERVER={SERVER};'
            f'DATABASE={DATABASE};'
            f'UID={USERNAME};'
            f'PWD={PASSWORD};'
            f'TrustServerCertificate=yes;'  # Importante para conexiones locales
            f'Encrypt=yes'                   # ODBC 18 requiere encrypt
        )
        
        print(f"Intentando conectar a: {SERVER}")
        print(f"Base de datos: {DATABASE}")
        
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Cambia 'tu_tabla' por el nombre real de tu tabla
        # Ejemplo: 'Clientes' o 'usuarios'
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
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 API Flask iniciada")
    print(f"📡 Conectando a SQL Server: {SERVER}")
    print(f"🔧 Driver: {DRIVER}")
    print("🧪 Prueba: http://localhost:5000/api/health")
    print("📊 Datos: http://localhost:5000/api/datos")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)