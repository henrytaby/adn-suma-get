"""
Configuración del sistema usando variables de entorno
"""
import os
from typing import Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field

# Cargar variables de entorno desde config.env
load_dotenv("config.env")

class Settings(BaseSettings):
    """Configuración del sistema"""
    
    # Configuración de autenticación
    nombre_usuario: str = Field(..., env="NOMBRE_USUARIO")
    password: str = Field(..., env="PASSWORD")
    url_b_sso: str = Field(..., env="URL_B_SSO")
    url_n_ingreso: str = Field(..., env="URL_N_INGRESO")
    size_list: int = Field(default=100, env="SIZE_LIST")
    
    # Configuración de la aplicación
    debug: bool = Field(default=True, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    output_dir: str = Field(default="output", env="OUTPUT_DIR")
    credentials_file: str = Field(default="credenciales.json", env="CREDENTIALS_FILE")
    verify_file: str = Field(default="verificar.json", env="VERIFY_FILE")
    
    # Configuración de requests
    request_timeout: int = Field(default=30, env="REQUEST_TIMEOUT")
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    retry_delay: int = Field(default=1, env="RETRY_DELAY")
    
    # Headers por defecto
    user_agent: str = Field(default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", env="USER_AGENT")
    accept_language: str = Field(default="es-ES,es;q=0.9,en;q=0.8", env="ACCEPT_LANGUAGE")
    
    # Configuración de MongoDB
    mongodb_uri: str = Field(default="mongodb://localhost:27017/", env="MONGODB_URI")
    mongodb_db: str = Field(default="suma", env="MONGODB_DB")
    mongodb_collection: str = Field(default="dim", env="MONGODB_COLLECTION")
    
    class Config:
        env_file = "config.env"
        case_sensitive = False

# Instancia global de configuración
settings = Settings()

def get_settings() -> Settings:
    """Obtener la configuración del sistema"""
    return settings 