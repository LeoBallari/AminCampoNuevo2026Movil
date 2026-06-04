from flask import Blueprint, request, jsonify
from database import obtener_conexion

despachos_bp = Blueprint('despachos', __name__)

@despachos_bp.route('/api/campañas', methods=['GET'])
def get_campanas():
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT [id_campaña], [nombre] FROM v2.Campañas ORDER BY nombre DESC")
        rows = cursor.fetchall()
        conn.close()
        return jsonify([{"id": row[0], "nombre": row[1]} for row in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@despachos_bp.route('/api/cultivos', methods=['GET'])
def get_cultivos():
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT id_cultivo, nombre_cultivo FROM v2.Cultivos ORDER BY nombre_cultivo")
        rows = cursor.fetchall()
        conn.close()
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
            SELECT E.id_entidad, E.razon_social, SUM(CP.neto_origen) / 100.0, COUNT(*)
            FROM v2.CartasPorte CP
            INNER JOIN v2.Entidades E ON CP.id_entregado = E.id_entidad
            WHERE CP.[id_campaña] = %s AND CP.id_cultivo = %s
            GROUP BY E.id_entidad, E.razon_social
            ORDER BY SUM(CP.neto_origen) DESC
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
            SELECT CP.Fecha,CP.nro_cp,CP.id_entregado, CP.ctg, CP.neto_origen,
                CASE 
                    WHEN CP.estado_cp = 'Certificada' THEN 'C'
                    WHEN CP.estado_cp = 'Confirmada' THEN 'T/OK'
                    ELSE 'S/C'
                END
            FROM v2.CartasPorte CP
            WHERE CP.[id_campaña] = %s AND CP.id_cultivo = %s AND CP.id_entregado = %s
            ORDER BY CP.fecha DESC
        """
        # Debug Extremo: Imprimir la query completa para ver si alguien inyectó id_lote
        full_query = query % (id_campana, id_cultivo, id_entidad)
        print(f"DEBUG QUERY: {full_query}")
        
        cursor.execute(query, (id_campana, id_cultivo, id_entidad))
        rows = cursor.fetchall()
        conn.close()
        return jsonify([{"fecha": r[0], "cp": r[1], "entidad": r[2], "ctg": r[3], "neto": float(r[4]), "estado": r[5]} for r in rows])
    except Exception as e:
        print(f"ERROR CRITICO: {str(e)}")
        return jsonify({"error": str(e), "query_ejecutada": query}), 500