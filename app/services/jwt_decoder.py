"""
Decodificador de JWT para extraer información del token
"""
import jwt
from typing import Dict, Any, Optional
from app.core.logger import app_logger
from app.core.exceptions import AuthenticationError

class JWTDecoder:
    """Decodificador de tokens JWT"""
    
    @staticmethod
    def decode_jwt(jwt_token: str) -> Dict[str, Any]:
        """Decodificar token JWT sin verificación de firma"""
        try:
            # Decodificar sin verificar la firma (solo para lectura)
            decoded = jwt.decode(jwt_token, options={"verify_signature": False})
            app_logger.debug("JWT decodificado exitosamente")
            return decoded
            
        except jwt.InvalidTokenError as e:
            app_logger.error(f"Error al decodificar JWT: {str(e)}")
            raise AuthenticationError(f"Token JWT inválido: {str(e)}")
        except Exception as e:
            app_logger.error(f"Error inesperado al decodificar JWT: {str(e)}")
            raise AuthenticationError(f"Error al decodificar JWT: {str(e)}")
    
    @staticmethod
    def extract_user_info(jwt_token: str) -> Dict[str, Any]:
        """Extraer información del usuario desde el JWT"""
        try:
            decoded = JWTDecoder.decode_jwt(jwt_token)
            
            # Extraer información relevante
            user_info = {
                "jti": decoded.get("jti"),  # ID del token
                "sub": decoded.get("sub"),  # Usuario
                "authorities": decoded.get("authorities", []),  # Roles/autoridades
                "iat": decoded.get("iat"),  # Fecha de emisión
                "exp": decoded.get("exp"),  # Fecha de expiración
                "origen": decoded.get("origen"),  # Origen
                "sistema": decoded.get("sistema")  # Sistema
            }
            
            app_logger.info(f"Información de usuario extraída: {user_info['sub']}")
            return user_info
            
        except Exception as e:
            app_logger.error(f"Error al extraer información del usuario: {str(e)}")
            raise AuthenticationError(f"Error al extraer información del usuario: {str(e)}")
    
    @staticmethod
    def is_token_expired(jwt_token: str) -> bool:
        """Verificar si el token JWT ha expirado"""
        try:
            decoded = JWTDecoder.decode_jwt(jwt_token)
            exp = decoded.get("exp")
            
            if not exp:
                app_logger.warning("Token JWT no tiene fecha de expiración")
                return True
            
            import time
            current_time = int(time.time())
            is_expired = current_time >= exp
            
            if is_expired:
                app_logger.warning("Token JWT ha expirado")
            else:
                app_logger.debug("Token JWT válido")
            
            return is_expired
            
        except Exception as e:
            app_logger.error(f"Error al verificar expiración del token: {str(e)}")
            return True 