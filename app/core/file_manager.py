"""
Gestor de archivos para manejar la persistencia de datos
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from app.config.settings import get_settings
from app.core.logger import app_logger
from app.core.exceptions import FileOperationError

class FileManager:
    """Gestor de archivos para el sistema"""
    
    def __init__(self):
        self.settings = get_settings()
        self.output_dir = Path(self.settings.output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def save_json(self, data: Dict[str, Any], filename: str, module: str = "general") -> str:
        """Guardar datos en formato JSON"""
        try:
            # Crear estructura de directorios por módulo y fecha
            today = datetime.now().strftime("%Y-%m-%d")
            module_dir = self.output_dir / module / today
            module_dir.mkdir(parents=True, exist_ok=True)
            
            # Generar nombre de archivo con timestamp
            timestamp = datetime.now().strftime("%H%M%S")
            file_path = module_dir / f"{filename}_{timestamp}.json"
            
            # Guardar archivo
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            app_logger.info(f"Archivo guardado: {file_path}")
            return str(file_path)
            
        except Exception as e:
            app_logger.error(f"Error al guardar archivo JSON {filename}: {str(e)}")
            raise FileOperationError(f"Error al guardar archivo JSON: {str(e)}")
    
    def load_json(self, filepath: str) -> Dict[str, Any]:
        """Cargar datos desde archivo JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            app_logger.debug(f"Archivo cargado: {filepath}")
            return data
            
        except Exception as e:
            app_logger.error(f"Error al cargar archivo JSON {filepath}: {str(e)}")
            raise FileOperationError(f"Error al cargar archivo JSON: {str(e)}")
    
    def save_credentials(self, credentials: Dict[str, Any]) -> str:
        """Guardar credenciales en archivo específico"""
        try:
            file_path = Path(self.settings.credentials_file)
            
            # Crear directorio si no existe
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(credentials, f, indent=2, ensure_ascii=False)
            
            app_logger.info(f"Credenciales guardadas: {file_path}")
            return str(file_path)
            
        except Exception as e:
            app_logger.error(f"Error al guardar credenciales: {str(e)}")
            raise FileOperationError(f"Error al guardar credenciales: {str(e)}")
    
    def load_credentials(self) -> Optional[Dict[str, Any]]:
        """Cargar credenciales desde archivo"""
        try:
            file_path = Path(self.settings.credentials_file)
            
            if not file_path.exists():
                app_logger.warning("Archivo de credenciales no encontrado")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                credentials = json.load(f)
            
            app_logger.debug("Credenciales cargadas exitosamente")
            return credentials
            
        except Exception as e:
            app_logger.error(f"Error al cargar credenciales: {str(e)}")
            raise FileOperationError(f"Error al cargar credenciales: {str(e)}")
    
    def save_verify_data(self, verify_data: Dict[str, Any]) -> str:
        """Guardar datos de verificación en archivo específico"""
        try:
            file_path = Path(self.settings.verify_file)
            
            # Crear directorio si no existe
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(verify_data, f, indent=2, ensure_ascii=False)
            
            app_logger.info(f"Datos de verificación guardados: {file_path}")
            return str(file_path)
            
        except Exception as e:
            app_logger.error(f"Error al guardar datos de verificación: {str(e)}")
            raise FileOperationError(f"Error al guardar datos de verificación: {str(e)}")
    
    def load_verify_data(self) -> Optional[Dict[str, Any]]:
        """Cargar datos de verificación desde archivo"""
        try:
            file_path = Path(self.settings.verify_file)
            
            if not file_path.exists():
                app_logger.warning("Archivo de verificación no encontrado")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                verify_data = json.load(f)
            
            app_logger.debug("Datos de verificación cargados exitosamente")
            return verify_data
            
        except Exception as e:
            app_logger.error(f"Error al cargar datos de verificación: {str(e)}")
            raise FileOperationError(f"Error al cargar datos de verificación: {str(e)}") 