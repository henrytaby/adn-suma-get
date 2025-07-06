"""
Servicio de autenticación para el sistema ADN
"""
from typing import Dict, Any, Optional
from app.config.settings import get_settings
from app.core.http_client import HTTPClient
from app.core.file_manager import FileManager
from app.core.logger import app_logger
from app.core.exceptions import AuthenticationError, APIError
from app.services.jwt_decoder import JWTDecoder

class AuthService:
    """Servicio de autenticación"""
    
    def __init__(self):
        self.settings = get_settings()
        self.http_client = HTTPClient()
        self.file_manager = FileManager()
        self.jwt_decoder = JWTDecoder()
    
    def authenticate(self) -> Dict[str, Any]:
        """Paso 1: Autenticación y recuperación de token"""
        try:
            app_logger.info("Iniciando proceso de autenticación...")
            
            # URL de autenticación
            auth_url = f"{self.settings.url_b_sso}/autenticar/portal?operador=undefined"
            
            # Headers específicos para autenticación
            headers = {
                "Content-Type": "application/json;charset=UTF-8",
                "Origin": "https://suma.aduana.gob.bo",
                "Referer": "https://suma.aduana.gob.bo/sso/indexLogin.html",
                "User": "cgalarza@aduana.gob.bo"
            }
            
            # Datos de autenticación
            auth_data = {
                "nombreUsuario": self.settings.nombre_usuario,
                "password": self.settings.password,
                "tipo": "INTERNO"
            }
            
            app_logger.debug(f"Enviando petición de autenticación a: {auth_url}")
            
            # Realizar petición POST
            response = self.http_client.post(auth_url, data=auth_data, headers=headers)
            auth_response = response.json()
            
            # Verificar respuesta
            if not auth_response.get("success"):
                error_msg = auth_response.get("message", "Error de autenticación desconocido")
                app_logger.error(f"Error en autenticación: {error_msg}")
                raise AuthenticationError(f"Error en autenticación: {error_msg}")
            
            result = auth_response.get("result", {})
            token = result.get("token")
            jwt_token = result.get("jwt")
            url = result.get("url")
            
            if not token or not jwt_token:
                app_logger.error("Token o JWT no encontrados en la respuesta")
                raise AuthenticationError("Token o JWT no encontrados en la respuesta")
            
            # Decodificar JWT para extraer información
            jwt_info = self.jwt_decoder.extract_user_info(jwt_token)
            
            # Preparar datos de credenciales
            credentials = {
                "authentication": {
                    "token": token,
                    "jwt": jwt_token,
                    "url": url,
                    "jwt_decoded": jwt_info,
                    "timestamp": auth_response.get("timestamp"),
                    "success": True
                },
                "user_info": {
                    "username": jwt_info.get("sub"),
                    "authorities": jwt_info.get("authorities", []),
                    "token_id": jwt_info.get("jti"),
                    "issued_at": jwt_info.get("iat"),
                    "expires_at": jwt_info.get("exp"),
                    "origen": jwt_info.get("origen"),
                    "sistema": jwt_info.get("sistema")
                }
            }
            
            # Guardar credenciales
            self.file_manager.save_credentials(credentials)
            
            # Guardar respuesta completa
            self.file_manager.save_json(auth_response, "authentication_response", "auth")
            
            app_logger.info(f"Autenticación exitosa para usuario: {jwt_info.get('sub')}")
            return credentials
            
        except Exception as e:
            app_logger.error(f"Error en proceso de autenticación: {str(e)}")
            raise AuthenticationError(f"Error en proceso de autenticación: {str(e)}")
    
    def get_credentials(self) -> Dict[str, Any]:
        """Paso 2: Obtener credenciales del portal"""
        try:
            app_logger.info("Obteniendo credenciales del portal...")
            
            # Cargar credenciales existentes
            credentials = self.file_manager.load_credentials()
            if not credentials:
                app_logger.warning("No se encontraron credenciales, iniciando autenticación...")
                credentials = self.authenticate()
            
            token = credentials["authentication"]["token"]
            
            # URL para obtener credenciales
            credentials_url = f"{self.settings.url_b_sso}/credentialPortal/{token}"
            
            # Headers específicos
            headers = {
                "Referer": "https://suma.aduana.gob.bo/portal/index.html",
                "Cookie": f"token={token}"
            }
            
            app_logger.debug(f"Obteniendo credenciales del portal: {credentials_url}")
            
            # Realizar petición GET
            response = self.http_client.get(credentials_url, headers=headers)
            credentials_response = response.json()
            
            # Verificar respuesta
            if not credentials_response.get("success"):
                error_msg = credentials_response.get("message", "Error al obtener credenciales")
                app_logger.error(f"Error al obtener credenciales: {error_msg}")
                raise AuthenticationError(f"Error al obtener credenciales: {error_msg}")
            
            # Actualizar credenciales con información del portal
            credentials["portal_credentials"] = credentials_response.get("result", {})
            
            # Guardar credenciales actualizadas
            self.file_manager.save_credentials(credentials)
            
            # Guardar respuesta completa
            self.file_manager.save_json(credentials_response, "credentials_response", "auth")
            
            app_logger.info("Credenciales del portal obtenidas exitosamente")
            return credentials
            
        except Exception as e:
            app_logger.error(f"Error al obtener credenciales del portal: {str(e)}")
            raise AuthenticationError(f"Error al obtener credenciales del portal: {str(e)}")
    
    def verify_token(self) -> Dict[str, Any]:
        """Paso 3: Verificar token"""
        try:
            app_logger.info("Verificando token...")
            
            # Cargar credenciales existentes
            credentials = self.file_manager.load_credentials()
            if not credentials:
                app_logger.warning("No se encontraron credenciales, iniciando autenticación...")
                credentials = self.authenticate()
            
            token = credentials["authentication"]["token"]
            
            # URL de verificación
            verify_url = f"{self.settings.url_b_sso}/autenticar/verificar/{token}"
            
            # Headers específicos
            headers = {
                "Referer": "https://suma.aduana.gob.bo/portal/index.html",
                "Cookie": f"token={token}"
            }
            
            app_logger.debug(f"Verificando token: {verify_url}")
            
            # Realizar petición GET
            response = self.http_client.get(verify_url, headers=headers)
            verify_response = response.json()
            
            # Verificar respuesta
            if not verify_response.get("success"):
                error_msg = verify_response.get("message", "Error al verificar token")
                app_logger.error(f"Error al verificar token: {error_msg}")
                raise AuthenticationError(f"Error al verificar token: {error_msg}")
            
            # Guardar datos de verificación
            self.file_manager.save_verify_data(verify_response.get("result", {}))
            
            # Guardar respuesta completa
            self.file_manager.save_json(verify_response, "verify_response", "auth")
            
            app_logger.info("Token verificado exitosamente")
            return verify_response.get("result", {})
            
        except Exception as e:
            app_logger.error(f"Error al verificar token: {str(e)}")
            raise AuthenticationError(f"Error al verificar token: {str(e)}")
    
    def full_auth_process(self) -> Dict[str, Any]:
        """Ejecutar proceso completo de autenticación (pasos 1, 2 y 3)"""
        try:
            app_logger.info("Iniciando proceso completo de autenticación...")
            
            # Paso 1: Autenticación
            credentials = self.authenticate()
            
            # Paso 2: Obtener credenciales del portal
            credentials = self.get_credentials()
            
            # Paso 3: Verificar token
            verify_data = self.verify_token()
            
            app_logger.info("Proceso completo de autenticación finalizado exitosamente")
            
            return {
                "credentials": credentials,
                "verify_data": verify_data,
                "status": "success"
            }
            
        except Exception as e:
            app_logger.error(f"Error en proceso completo de autenticación: {str(e)}")
            raise AuthenticationError(f"Error en proceso completo de autenticación: {str(e)}")
        finally:
            # Cerrar cliente HTTP
            self.http_client.close()
    
    def check_auth_status(self) -> bool:
        """Verificar si la autenticación está vigente"""
        try:
            credentials = self.file_manager.load_credentials()
            if not credentials:
                return False
            
            jwt_token = credentials["authentication"]["jwt"]
            
            # Verificar si el token ha expirado
            if self.jwt_decoder.is_token_expired(jwt_token):
                app_logger.warning("Token JWT ha expirado")
                return False
            
            app_logger.info("Autenticación vigente")
            return True
            
        except Exception as e:
            app_logger.error(f"Error al verificar estado de autenticación: {str(e)}")
            return False 