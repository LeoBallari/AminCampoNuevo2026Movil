from flask import Blueprint, request, jsonify
from database import obtener_conexion

lotes_bp = Blueprint('lotes', __name__)

@lotes_bp.route('/api/campañas', methods=['GET'])
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


@lotes_bp.route('/api/lotes', methods=['GET'])
def get_lotes():
    id_campana = request.args.get('id_campana')
    
    if not id_campana:
        return jsonify([])

    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        query = """
            SELECT 
                b.nombre_bloque,
                b.has_bloque,
                ROUND(SUM(CASE WHEN l.condicion = 'Propio' THEN l.ha_reales ELSE 0 END) * 100.0 / NULLIF(SUM(l.ha_reales), 0), 2) AS porcentaje_propia,
                ROUND(SUM(CASE WHEN l.condicion = 'Arrendado' THEN l.ha_reales ELSE 0 END) * 100.0 / NULLIF(SUM(l.ha_reales), 0), 2) AS porcentaje_arrendada
            
            FROM v2.BloquesProduccion bp
            INNER JOIN v2.Bloques b ON bp.id_bloque = b.id_bloque
            INNER JOIN v2.Campañas c ON bp.id_campaña = c.id_campaña
            INNER JOIN v2.Bloque_lotes bl ON b.id_bloque = bl.id_bloque
            INNER JOIN v2.Lotes l ON bl.id_lote = l.id_lote
            
            WHERE bp.id_campaña = %s

            GROUP BY b.has_bloque, b.nombre_bloque, c.nombre ORDER BY b.nombre_bloque
        """
        cursor.execute(query, (id_campana,))
        rows = cursor.fetchall()
        conn.close()
        return jsonify([{
            "bloque": r[0],
            "has": r[1],
            "% Propio": r[2],
            "% Arrendado": r[3],
        } for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
