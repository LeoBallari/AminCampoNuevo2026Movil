from flask import Blueprint, request, jsonify
from database import obtener_conexion

cosecha_bp = Blueprint('cosecha', __name__)

@cosecha_bp.route('/api/campañas', methods=['GET'])
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

@cosecha_bp.route('/api/cultivos', methods=['GET'])
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

@cosecha_bp.route('/api/cosecha/resumen', methods=['GET'])
def get_cosecha_resumen():
    id_campana = request.args.get('id_campana')
    id_cultivo = request.args.get('id_cultivo')
    
    if not id_campana or not id_cultivo:
        return jsonify([])

    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        query = """
            SELECT 
                COALESCE(B_BP.nombre_bloque, B_100.nombre_bloque, B_140.nombre_bloque, B_200.nombre_bloque) AS nombre_bloque, 
                TC.estadio,
				O.variedades AS variedad,
                COALESCE(SUM(CD.neto_final) / 100, 0) / NULLIF(TC.has, 0) AS rinde_promedio,
                CASE 
                    WHEN SUM(CD.neto_final) > 0 
                    THEN COALESCE(SUM(COALESCE(MH.humedad, 0) * CD.neto_final) / SUM(CD.neto_final), 0)
                    ELSE 0 
                END AS humedad_promedio,
                TC.has
            FROM v2.TareaCosecha AS TC 
            LEFT JOIN v2.Cultivos CUL ON TC.id_cultivo = CUL.id_cultivo
            LEFT JOIN v2.Campañas C ON TC.id_campaña = C.id_campaña 
            LEFT JOIN v2.BloquesProduccion BP ON TC.id_bloque_produccion = BP.id_bloque_produccion
            LEFT JOIN v2.Bloques B_BP ON BP.id_bloque = B_BP.id_bloque
            LEFT JOIN v2.Bloques B_100 ON TC.id_bloque_produccion - 100 = B_100.id_bloque
            LEFT JOIN v2.Bloques B_140 ON TC.id_bloque_produccion - 140 = B_140.id_bloque
            LEFT JOIN v2.Bloques B_200 ON TC.id_bloque_produccion - 200 = B_200.id_bloque
            LEFT JOIN v2.Maquinarias M ON TC.id_maquinaria = M.id_maquinaria 
            LEFT JOIN v2.TareaCosecha_Detalle AS CD ON TC.id_cosecha = CD.id_cosecha
            LEFT JOIN v2.MermasHumedad AS MH ON CD.id_merma_humedad = MH.id_merma
            OUTER APPLY (
                SELECT STUFF((
                    SELECT ', ' + I.nombre_comercial
                    FROM v2.TareaSiembra TS2
                    JOIN v2.TareaSiembra_Detalle TSD2 ON TS2.id_siembra = TSD2.id_siembra
                    JOIN v2.Insumos I ON TSD2.id_insumo = I.id_insumo
                    WHERE TS2.id_bloque_produccion = TC.id_bloque_produccion
                    AND TS2.id_cultivo = TC.id_cultivo
                    AND TS2.id_campaña = TC.id_campaña
                    AND I.id_categoria_insumo IN (5, 6)
                    ORDER BY TS2.fecha
                    FOR XML PATH(''), TYPE
                ).value('.', 'NVARCHAR(MAX)'), 1, 2, '') AS variedades
            ) O
            WHERE TC.id_campaña = %s AND TC.id_cultivo = %s
            GROUP BY 
                TC.id_cosecha,
                COALESCE(B_BP.nombre_bloque, B_100.nombre_bloque, B_140.nombre_bloque, B_200.nombre_bloque), 
                M.descripcion, TC.estadio, TC.has,  
                CUL.nombre_cultivo, O.variedades
            ORDER BY TC.id_cosecha;
        """
        cursor.execute(query, (id_campana, id_cultivo))
        rows = cursor.fetchall()
        conn.close()
        return jsonify([{"bloque": r[0], "estadio": r[1], "variedad": r[2], "rinde": r[3], "humedad": r[4], "has": float(r[5])} 
                        for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
