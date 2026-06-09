from flask import Blueprint, request, jsonify
from database import obtener_conexion

estadisticas_bp = Blueprint('estadisticas', __name__)

@estadisticas_bp.route('/api/estadisticas/lotes', methods=['GET'])
def get_campos_fisicos():
    """Retorna la lista de campos físicos que tienen cosecha registrada."""
    query = """
        SELECT DISTINCT
            cf.id_campo_fisico,
            cf.nombre_campo
        FROM 
            v2.CamposFisicos cf
        INNER JOIN 
            v2.Bloques b ON cf.id_campo_fisico = b.id_campo_fisico
        INNER JOIN 
            v2.BloquesProduccion bp ON b.id_bloque = bp.id_bloque AND bp.activo = 1
        INNER JOIN 
            v2.TareaCosecha tc ON bp.id_bloque_produccion = tc.id_bloque_produccion
        WHERE 
            cf.activo = 1
            AND tc.id_cosecha IS NOT NULL
        ORDER BY 
            cf.nombre_campo
    """
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return jsonify([{"id": row[0], "nombre": row[1]} for row in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@estadisticas_bp.route('/api/cultivos', methods=['GET'])
def get_cultivos():
    """Retorna la lista de cultivos activos."""
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT id_cultivo, nombre_cultivo FROM v2.Cultivos WHERE activo = 1 ORDER BY nombre_cultivo")
        rows = cursor.fetchall()
        conn.close()
        return jsonify([{"id": row[0], "nombre": row[1]} for row in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@estadisticas_bp.route('/api/estadisticas', methods=['GET'])
def get_estadisticas():
    """
    Retorna estadísticas de rendimiento para campos físicos seleccionados.
    Parámetros:
        lotes_ids: IDs de campos físicos separados por coma (ej: "1,2,3")
        id_cultivo: ID del cultivo (ej: 1)
    """
    lotes_ids_raw = request.args.get('lotes_ids')
    id_cultivo_raw = request.args.get('id_cultivo')
    
    if not id_cultivo_raw or not lotes_ids_raw:
        return jsonify([])

    try:
        id_cultivo = int(id_cultivo_raw)
        lotes_ids = [int(x.strip()) for x in lotes_ids_raw.split(',') if x.strip()]
        
        if not lotes_ids:
            return jsonify([])

        # Generar marcadores de posición dinámicos (%s, %s, ...)
        placeholders = ', '.join(['%s'] * len(lotes_ids))

        query = f"""
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
            ),
            DatosAgrupados AS (
                SELECT 
                    c.id_campaña,
                    c.nombre AS CAMPAÑA,
                    cf.nombre_campo AS CAMPO,
                    cu.id_cultivo,
                    cu.nombre_cultivo AS CULTIVO,
                    SUM(ct.total_kg) AS TOTAL_KG,
                    SUM(ct.has) AS TOTAL_HECTAREAS,
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
                    v2.CamposFisicos cf ON b.id_campo_fisico = cf.id_campo_fisico
                INNER JOIN 
                    v2.Cultivos cu ON ct.id_cultivo = cu.id_cultivo
                WHERE 
                    cu.id_cultivo = %s
                    AND cf.id_campo_fisico IN ({placeholders})
                GROUP BY 
                    c.id_campaña, c.nombre, cf.nombre_campo, cu.id_cultivo, cu.nombre_cultivo
            )
            SELECT 
                CAMPAÑA,
                STUFF((
                    SELECT ', ' + CAMPO
                    FROM DatosAgrupados d2
                    WHERE d2.id_campaña = d1.id_campaña
                    AND d2.id_cultivo = d1.id_cultivo
                    FOR XML PATH('')
                ), 1, 2, '') AS CAMPOS,
                CULTIVO,
                SUM(TOTAL_KG) AS TOTAL_KG,
                SUM(TOTAL_HECTAREAS) AS TOTAL_HECTAREAS,
                CAST(ROUND((SUM(TOTAL_KG) / NULLIF(SUM(TOTAL_HECTAREAS), 0)) / 100.0, 2) AS DECIMAL(10,2)) AS RINDE_PROMEDIO_QQ_HAS,
                SUM(CANTIDAD_COSECHAS) AS CANTIDAD_COSECHAS
            FROM 
                DatosAgrupados d1
            GROUP BY 
                id_campaña, CAMPAÑA, id_cultivo, CULTIVO
            ORDER BY 
                CAMPAÑA;
        """

        conn = obtener_conexion()
        cursor = conn.cursor()
        
        # Parámetros: id_cultivo + lista de IDs de campos físicos
        params = [id_cultivo] + lotes_ids
        cursor.execute(query, params)
        
        rows = cursor.fetchall()
        conn.close()
        
        return jsonify([{
            "campaña": r[0],
            "campo": r[1],
            "cultivo": r[2],
            "total_kg": float(r[3]) if r[3] is not None else 0.0,
            "has": float(r[4]) if r[4] is not None else 0.0,
            "rinde": float(r[5]) if r[5] is not None else 0.0,
            "cantidad": r[6]
        } for r in rows])
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500