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

@app.route('/api/campañas', methods=['GET'])
def get_campanas():
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        # Traemos el ID y el Nombre
        cursor.execute("SELECT id_campaña, nombre FROM v2.Campañas ORDER BY nombre DESC")
        rows = cursor.fetchall()
        conn.close()
        # Devolvemos una lista de diccionarios
        return jsonify([{"id": row[0], "nombre": row[1]} for row in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/cultivos', methods=['GET'])
def get_cultivos():
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        # Traemos el ID y el Nombre
        cursor.execute("SELECT id_cultivo, nombre_cultivo FROM v2.Cultivos ORDER BY nombre_cultivo")
        rows = cursor.fetchall()
        conn.close()
        # Devolvemos una lista de diccionarios
        return jsonify([{"id": row[0], "nombre": row[1]} for row in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/despachos/resumen', methods=['GET'])
def get_despachos_resumen():
    id_campana = request.args.get('id_campana')
    id_cultivo = request.args.get('id_cultivo')
    
    if not id_campana or not id_cultivo:
        return jsonify([])

    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        query = """
            SELECT 
                E.id_entidad,
                E.razon_social, 
                SUM(CP.neto_origen) / 100.0 as total_qq, 
                COUNT(*) as cantidad
            FROM v2.CartasPorte CP

            INNER JOIN v2.Entidades E ON CP.id_entregado = E.id_entidad
            WHERE CP.id_campaña = %s AND CP.id_cultivo = %s
            GROUP BY E.id_entidad, E.razon_social
            ORDER BY total_qq DESC
        """
        cursor.execute(query, (id_campana, id_cultivo))
        rows = cursor.fetchall()
        conn.close()
        return jsonify([{"id": r[0], "entidad": r[1], "qq": float(r[2]), "cantidad": r[3]} for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/despachos/detalle', methods=['GET'])
def get_despachos_detalle():
    id_campana = request.args.get('id_campana')
    id_cultivo = request.args.get('id_cultivo')
    id_entidad = request.args.get('id_entidad')

    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        # Nota: Ajusté los nombres de campos asumiendo una estructura estándar, 
        # podrías necesitar ajustarlos según tu esquema real de v2.CartasPorte
        query = """
            SELECT 
                CONVERT(VARCHAR, CP.fecha, 103) as fecha,
                ISNULL(L.nombre, 'S/D') as lote,
                CP.neto_origen,
                ISNULL(D.nombre_destino, 'S/D') as destino
            FROM v2.CartasPorte CP
            LEFT JOIN v2.Lotes L ON CP.id_lote = L.id_lote
            LEFT JOIN v2.Destinos D ON CP.id_destino = D.id_destino
            WHERE CP.id_campaña = %s AND CP.id_cultivo = %s AND CP.id_entregado = %s
            ORDER BY CP.fecha DESC
        """
        cursor.execute(query, (id_campana, id_cultivo, id_entidad))
        rows = cursor.fetchall()
        conn.close()
        return jsonify([{"fecha": r[0], "lote": r[1], "neto": float(r[2]), "destino": r[3]} for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)