from flask import Blueprint, request, jsonify
from database import obtener_conexion

estadisticas_bp = Blueprint('estadisticas', __name__)

@estadisticas_bp.route('/api/estadisticas/lotes', methods=['GET'])
def get_lotes_unificados():
    query0 = """
        SELECT DISTINCT Nombre
        FROM (
            SELECT nombre_lote AS Nombre FROM v2.Lotes WHERE nombre_lote IS NOT NULL
            UNION
            SELECT nombre_bloque AS Nombre FROM v2.Bloques WHERE nombre_bloque IS NOT NULL
        ) AS NombresUnificados
        WHERE Nombre <> ''
        ORDER BY Nombre;
    """
    query = """
        SELECT DISTINCT
            Nombre
        FROM (
            -- Lotes que tienen cosecha
            SELECT DISTINCT
                l.nombre_lote AS Nombre
            FROM 
                v2.Lotes l
            INNER JOIN 
                v2.Bloque_Lotes bl ON l.id_lote = bl.id_lote
            INNER JOIN 
                v2.BloquesProduccion bp ON bl.id_bloque = bp.id_bloque AND bp.activo = 1
            INNER JOIN 
                v2.TareaCosecha tc ON bp.id_bloque_produccion = tc.id_bloque_produccion
            
            UNION
            
            -- Bloques que tienen cosecha
            SELECT DISTINCT
                b.nombre_bloque AS Nombre
            FROM 
                v2.Bloques b
            INNER JOIN 
                v2.BloquesProduccion bp ON b.id_bloque = bp.id_bloque AND bp.activo = 1
            INNER JOIN 
                v2.TareaCosecha tc ON bp.id_bloque_produccion = tc.id_bloque_produccion
        ) AS NombresConCosecha
        WHERE 
            Nombre IS NOT NULL AND Nombre <> ''
        ORDER BY 
            Nombre;    
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
    lotes_raw = request.args.get('lotes')
    id_cultivo = request.args.get('id_cultivo')
    
    if not id_cultivo or not lotes_raw:
        return jsonify([])

    try:
        # Procesar la lista de lotes recibida por coma (CSV)
        lotes_list = [x.strip() for x in lotes_raw.split(',') if x.strip()]
        if not lotes_list:
            return jsonify([])

        # Generar marcadores de posición dinámicos (%s, %s, ...)
        placeholders = ', '.join(['%s'] * len(lotes_list))

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
            ),
            DatosAgrupados AS (
                SELECT 
                    c.id_campaña,
                    c.nombre AS CAMPAÑA,
                    b.nombre_bloque AS BLOQUE,
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
                    v2.Cultivos cu ON ct.id_cultivo = cu.id_cultivo
                WHERE 
                    cu.nombre_cultivo = %s
                    AND (
                        b.nombre_bloque IN ({placeholders})
                        OR EXISTS (
                            SELECT 1 
                            FROM v2.Bloque_Lotes bl 
                            INNER JOIN v2.Lotes l ON bl.id_lote = l.id_lote
                            WHERE bl.id_bloque = b.id_bloque 
                            AND l.nombre_lote IN ({placeholders})
                        )
                    )
                GROUP BY 
                    c.id_campaña, c.nombre, b.nombre_bloque, cu.id_cultivo, cu.nombre_cultivo
            )
            SELECT 
                CAMPAÑA,
                STUFF((
                    SELECT ', ' + BLOQUE
                    FROM DatosAgrupados d2
                    WHERE d2.id_campaña = d1.id_campaña
                    AND d2.id_cultivo = d1.id_cultivo
                    FOR XML PATH('')
                ), 1, 2, '') AS BLOQUES,
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
        """.replace("{placeholders}", placeholders)

        conn = obtener_conexion()
        cursor = conn.cursor()

        # Parámetros: cultivo + lista de lotes (para el bloque) + lista de lotes (para el lote individual)
        params = [id_cultivo] + lotes_list + lotes_list
        cursor.execute(query, params)
        
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
