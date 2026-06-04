"""
Configuración y conexión centralizada a SQL Server
"""
import pymssql

SERVER = '190.103.87.151'        
PORT = 12433                     
DATABASE = 'Campo_LaReforma'  
USERNAME = 'lballari'     
PASSWORD = 'Clave.1369'  

def obtener_conexion():
    """Retorna una nueva conexión limpia a la base de datos"""
    return pymssql.connect(
        server=SERVER,
        port=PORT,
        user=USERNAME,
        password=PASSWORD,
        database=DATABASE,
        login_timeout=10,
        timeout=10,
        tds_version='7.0'  # Mantiene la compatibilidad nativa jTDS
    )