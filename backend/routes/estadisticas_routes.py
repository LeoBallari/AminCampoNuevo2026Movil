from flask import Blueprint, request, jsonify
from database import obtener_conexion

estadisticas_bp = Blueprint('estadisticas', __name__)

@estadisticas_bp.route('/api/lotes', methods=['GET'])
def get_lotes_unificados():
    query = """
        SELECT DISTINCT Nombre
        FROM (
            SELECT nombre_lote AS Nombre FROM v2.Lotes
            UNION
            SELECT nombre_bloque AS Nombre FROM v2.Bloques
        ) AS NombresUnificados
        ORDER BY Nombre;    
    """
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return jsonify([{"id": row[0], "nombre": row[0]} for row in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@estadisticas_bp.route('/api/cultivos', methods=['GET'])
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

@estadisticas_bp.route('/api/estadisticas', methods=['GET'])
def get_estadisticas():
    lote = request.args.get('id_campana')
    id_cultivo = request.args.get('id_cultivo')
    
    if not id_cultivo or not lote:
        return jsonify([])

    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        # DECLARE @nombre VARCHAR(100) = 'quiroga';  -- Lo que elige el usuario
        # DECLARE @cultivo_nombre VARCHAR(50) = 'maiz';       -- Lo que elige el usuario
            
        query = """
            WITH CosechaTotal AS (
                SELECT 
                    tc.id_cosecha,
                    tc.id_bloque_produccion,
                    tc.has,
                    tc.id_cultivo,
                    SUM(tcd.neto_final) AS total_kg
                FROM 
                    v2.TareaCosecha tc
                INNER JOIN 
                    v2.TareaCosecha_Detalle tcd ON tc.id_cosecha = tcd.id_cosecha
                WHERE 
                    tc.id_cosecha IS NOT NULL
                    AND tc.has > 0
                GROUP BY 
                    tc.id_cosecha, tc.id_bloque_produccion, tc.has, tc.id_cultivo
            )
            SELECT 
                c.nombre AS CAMPAÑA,
                b.nombre_bloque AS BLOQUE,
                cu.nombre_cultivo AS CULTIVO,
                SUM(ct.total_kg) AS TOTAL_KG,
                AVG(ct.has) AS TOTAL_HECTAREAS,
                CAST(ROUND((SUM(ct.total_kg) / NULLIF(AVG(ct.has), 0)) / 100.0, 2) AS DECIMAL(10,2)) AS RINDE_QQ_HAS,
                COUNT(DISTINCT ct.id_cosecha) AS CANTIDAD_COSECHAS
            FROM 
                CosechaTotal ct
            INNER JOIN 
                v2.BloquesProduccion bp ON ct.id_bloque_produccion = bp.id_bloque_produccion AND bp.activo = 1
            INNER JOIN 
                v2.Campañas c ON bp.id_campaña = c.id_campaña
            INNER JOIN 
                v2.Bloques b ON bp.id_bloque = b.id_bloque
            INNER JOIN 
                v2.Cultivos cu ON ct.id_cultivo = cu.id_cultivo
            WHERE 
                cu.nombre_cultivo = %s
                AND (
                    b.nombre_bloque = %s
                    OR EXISTS (
                        SELECT 1 
                        FROM v2.Bloque_Lotes bl 
                        INNER JOIN v2.Lotes l ON bl.id_lote = l.id_lote
                        WHERE bl.id_bloque = b.id_bloque AND l.nombre_lote = %s
                    )
                )
            GROUP BY 
                c.nombre, b.nombre_bloque, cu.nombre_cultivo
            ORDER BY 
                c.nombre;
        """
        # Se necesitan 3 parámetros para los 3 '%s' en el WHERE
        cursor.execute(query, (id_cultivo, lote, lote))
        rows = cursor.fetchall()
        conn.close()
        return jsonify([{
            "campaña": r[0],
            "bloque": r[1],
            "cultivo": r[2],
            "total_kg": float(r[3]) if r[3] is not None else 0.0,
            "has": float(r[4]) if r[4] is not None else 0.0,
            "rinde": float(r[5]) if r[5] is not None else 0.0,
            "cantidad": r[6]
        } for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
