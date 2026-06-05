from flask import Blueprint, request, jsonify
from database import obtener_conexion

siembra_bp = Blueprint('siembra', __name__)

@siembra_bp.route('/api/campañas', methods=['GET'])
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

@siembra_bp.route('/api/cultivos', methods=['GET'])
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

@siembra_bp.route('/api/siembra/resumen', methods=['GET'])
def get_siembra_resumen():
    id_campana = request.args.get('id_campana')
    id_cultivo = request.args.get('id_cultivo')
    
    if not id_campana or not id_cultivo:
        return jsonify([])

    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        query = """
            SELECT 
                TS.fecha AS fecha,
                B.nombre_bloque AS bloque,
                TS.has,
                TS.estadio,
                O.insumos
            FROM v2.TareaSiembra AS TS
            LEFT JOIN v2.Campañas          C   ON TS.id_campaña           = C.id_campaña
            LEFT JOIN v2.Cultivos          CUL ON TS.id_cultivo           = CUL.id_cultivo
            LEFT JOIN v2.BloquesProduccion BP  ON TS.id_bloque_produccion = BP.id_bloque_produccion
            LEFT JOIN v2.Bloques           B   ON BP.id_bloque            = B.id_bloque
            LEFT JOIN v2.Entidades         E   ON TS.id_entidad           = E.id_entidad
            LEFT JOIN v2.Maquinarias       M1  ON TS.id_maquinaria1       = M1.id_maquinaria
            LEFT  JOIN v2.Maquinarias       M2  ON TS.id_maquinaria2       = M2.id_maquinaria
            OUTER APPLY (
                SELECT STUFF((
                    SELECT ', ' + I.nombre_comercial + ' ' + CAST(SD.dosis AS NVARCHAR)
                    FROM v2.TareaSiembra_Detalle SD
                    JOIN v2.Insumos I ON SD.id_insumo = I.id_insumo
                    WHERE SD.id_siembra = TS.id_siembra
                    ORDER BY I.nombre_comercial
                    FOR XML PATH(''), TYPE
                ).value('.', 'NVARCHAR(MAX)'), 1, 2, '') AS insumos
            ) O
            WHERE TS.id_campaña = %s
            AND TS.id_cultivo = %s
            ORDER BY TS.id_siembra;
        """
        cursor.execute(query, (id_campana, id_cultivo))
        rows = cursor.fetchall()
        conn.close()
        return jsonify([{
            "fecha": r[0].isoformat() if r[0] else None,
            "bloque": r[1],
            "has": r[2],
            "estadio": r[3],
            "insumos": r[4] or "",
        } for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
