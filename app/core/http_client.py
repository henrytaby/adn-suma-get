"""
Cliente HTTP base con manejo de errores y reintentos
"""
import time
import requests
from typing import Dict, Any, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from app.config.settings import get_settings
from app.core.logger import app_logger
from app.core.exceptions import APIError

class HTTPClient:
    """Cliente HTTP con configuración y manejo de errores"""
    
    def __init__(self):
        self.settings = get_settings()
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Crear sesión HTTP con configuración de reintentos"""
        session = requests.Session()
        
        # Configurar reintentos
        retry_strategy = Retry(
            total=self.settings.max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
            backoff_factor=self.settings.retry_delay
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Configurar headers por defecto
        session.headers.update({
            "User-Agent": self.settings.user_agent,
            "Accept-Language": self.settings.accept_language,
            "Accept": "application/json, text/plain, */*",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache"
        })
        
        return session
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Obtener headers por defecto"""
        return {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": self.settings.accept_language,
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        }
    
    def get(self, url: str, headers: Optional[Dict[str, str]] = None, **kwargs) -> requests.Response:
        """Realizar petición GET"""
        try:
            headers = {**self._get_default_headers(), **(headers or {})}
            app_logger.debug(f"GET {url}")
            
            response = self.session.get(
                url, 
                headers=headers, 
                timeout=self.settings.request_timeout,
                **kwargs
            )
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            app_logger.error(f"Error en petición GET {url}: {str(e)}")
            raise APIError(f"Error en petición GET: {str(e)}")
    
    def post(self, url: str, data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, **kwargs) -> requests.Response:
        """Realizar petición POST"""
        try:
            headers = {**self._get_default_headers(), **(headers or {})}
            app_logger.debug(f"POST {url}")
            
            response = self.session.post(
                url, 
                json=data,
                headers=headers, 
                timeout=self.settings.request_timeout,
                **kwargs
            )
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            app_logger.error(f"Error en petición POST {url}: {str(e)}")
            raise APIError(f"Error en petición POST: {str(e)}")
    
    def close(self):
        """Cerrar la sesión HTTP"""
        self.session.close() 