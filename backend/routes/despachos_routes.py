from flask import Blueprint, jsonify, request
from database import obtener_conexion  # Importamos la conexión centralizada

# Creamos el Blueprint para el módulo de cereales y despachos
despachos_bp = Blueprint('despachos', __name__)

@despachos_bp.route('/api/campañas', methods=['GET'])
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

@despachos_bp.route('/api/cultivos', methods=['GET'])
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

@despachos_bp.route('/api/despachos/resumen', methods=['GET'])
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

@despachos_bp.route('/api/despachos/detalle', methods=['GET'])
def get_despachos_detalle():
    id_campana = request.args.get('id_campana')
    id_cultivo = request.args.get('id_cultivo')
    id_entidad = request.args.get('id_entidad')

    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
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