"""
Servicio de autenticación
Maneja todas las llamadas a la API de login
"""
import httpx
from config import API_URL, API_TIMEOUT


class AuthService:
    """Servicio para manejar autenticación con el backend"""
    
    @staticmethod
    def login(usuario: str, contraseña: str) -> dict:
        """
        Intenta hacer login con las credenciales proporcionadas.
        
        Args:
            usuario: Nombre de usuario
            contraseña: Contraseña
            
        Returns:
            dict: {'success': bool, 'message': str, 'status_code': int}
        """
        try:
            payload = {"usuario": usuario, "contraseña": contraseña}
            print(f"Enviando petición a: {API_URL}/api/login")
            
            response = httpx.post(
                f"{API_URL}/api/login",
                json=payload,
                timeout=API_TIMEOUT
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': '✅ ¡Acceso Concedido!',
                    'status_code': 200
                }
            elif response.status_code == 401:
                return {
                    'success': False,
                    'message': '❌ Usuario o clave incorrectos',
                    'status_code': 401
                }
            else:
                return {
                    'success': False,
                    'message': f'⚠️ Error del servidor: {response.status_code}',
                    'status_code': response.status_code
                }
                
        except httpx.TimeoutException:
            return {
                'success': False,
                'message': '❌ Tiempo de espera agotado.\nEl servidor demoró demasiado en responder.',
                'status_code': 0
            }
        except Exception as err:
            return {
                'success': False,
                'message': f'❌ Error de red: {str(err)}',
                'status_code': 0
            }
