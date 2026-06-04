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
        # Usamos Alias (AS) para que las llaves del JSON coincidan siempre
        query = """
            SELECT T.[fecha], T.[nro_cp] AS cp, T.[ctg], T.[neto_origen] AS neto, 
                E1.[razon_social] AS destino, E2.[razon_social] AS transporte, 
                T.[pat_chasis] AS patente, T.[estado_cp] as estado
            FROM v2.CartasPorte AS T
            LEFT JOIN v2.Entidades AS E1 ON T.id_destino = E1.id_entidad
            LEFT JOIN v2.Entidades AS E2 ON T.id_transportista = E2.id_entidad
            WHERE T.[id_campaña] = %s AND T.id_cultivo = %s AND T.id_entregado = %s
            ORDER BY T.fecha DESC
        """
        cursor.execute(query, (id_campana, id_cultivo, id_entidad))
        rows = cursor.fetchall()
        
        # Obtener nombres de columnas dinámicamente
        columns = [column[0] for column in cursor.description]
        conn.close()
        
        resultado = []
        for r in rows:
            # Creamos el diccionario uniendo nombres de columnas con valores
            d = dict(zip(columns, r))
            # Formateo de tipos
            d['fecha'] = str(d['fecha'])
            d['neto'] = float(d['neto']) if d['neto'] else 0
            d['cp'] = str(d['cp']).strip() if d['cp'] else ""
            d['destino'] = d['destino'].strip() if d['destino'] else "N/A"
            d['transporte'] = d['transporte'].strip() if d['transporte'] else "N/A"
            d['v'] = "2.0" # NUEVA VERSION
            resultado.append(d)
            
        return jsonify(resultado)
    except Exception as e:
        error_str = str(e)
        print(f"ERROR CRITICO EN DETALLE: {error_str}")
        # Si el error persiste, devolvemos información extra para depurar
        return jsonify({
            "error": error_str, 
            "info": "Error en la consulta de detalle de cartas de porte"
        }), 500