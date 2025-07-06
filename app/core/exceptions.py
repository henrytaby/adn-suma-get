"""
Excepciones personalizadas del sistema
"""

class ADNException(Exception):
    """Excepción base para el sistema ADN"""
    pass

class AuthenticationError(ADNException):
    """Error de autenticación"""
    pass

class APIError(ADNException):
    """Error en la comunicación con la API"""
    pass

class ConfigurationError(ADNException):
    """Error de configuración"""
    pass

class DataProcessingError(ADNException):
    """Error en el procesamiento de datos"""
    pass

class FileOperationError(ADNException):
    """Error en operaciones de archivos"""
    pass 