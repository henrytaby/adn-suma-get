"""
Sistema de logging configurado
"""
import sys
from pathlib import Path
from loguru import logger
from app.config.settings import get_settings

def setup_logger():
    """Configurar el sistema de logging"""
    settings = get_settings()
    
    # Remover logger por defecto
    logger.remove()
    
    # Configurar logger para consola
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True
    )
    
    # Configurar logger para archivo
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger.add(
        log_dir / "app_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.log_level,
        rotation="1 day",
        retention="30 days",
        compression="zip"
    )
    
    return logger

# Configurar logger al importar el módulo
app_logger = setup_logger() 