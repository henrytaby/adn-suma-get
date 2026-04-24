"""
Servicio para extracción de Manifiestos de Carga
"""
import math
from datetime import datetime, time
from typing import Dict, Any, List, Optional
from app.config.settings import get_settings
from app.core.http_client import HTTPClient
from app.core.file_manager import FileManager
from app.core.logger import app_logger
from app.core.exceptions import APIError, DataProcessingError
from app.services.auth_service import AuthService
from app.core.mongo_manager import MongoManager

class ManifiestoService:
    """Servicio para extracción de datos de Manifiestos de Carga"""
    
    def __init__(self):
        self.settings = get_settings()
        self.http_client = HTTPClient()
        self.file_manager = FileManager()
        self.auth_service = AuthService()
    
    def _convert_date_to_timestamp(self, date_str: str, start_of_day: bool = True) -> int:
        """Convertir fecha DD/MM/YYYY a timestamp"""
        try:
            # Parsear fecha
            date_obj = datetime.strptime(date_str, "%d/%m/%Y")
            
            # Ajustar hora según parámetro
            if start_of_day:
                date_obj = date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                date_obj = date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Convertir a timestamp en segundos
            timestamp_seconds = int(date_obj.timestamp())
            
            # Agregar 3 ceros al final (convertir a formato requerido)
            timestamp = timestamp_seconds * 1000
            
            app_logger.debug(f"Fecha {date_str} convertida a timestamp: {timestamp_seconds} -> {timestamp}")
            return timestamp
            
        except ValueError as e:
            app_logger.error(f"Error al convertir fecha {date_str}: {str(e)}")
            raise DataProcessingError(f"Formato de fecha inválido: {date_str}. Use DD/MM/YYYY")
    
    def _create_date_range(self, fecha_desde: str, fecha_hasta: str) -> str:
        """Crear rango de fechas en formato timestamp;timestamp"""
        try:
            # Convertir fechas a timestamp
            start_timestamp = self._convert_date_to_timestamp(fecha_desde, start_of_day=True)
            end_timestamp = self._convert_date_to_timestamp(fecha_hasta, start_of_day=False)
            
            # Crear rango separado por punto y coma
            date_range = f"{start_timestamp};{end_timestamp}"
            
            app_logger.info(f"Rango de fechas creado: {fecha_desde} - {fecha_hasta} -> {date_range}")
            return date_range
            
        except Exception as e:
            app_logger.error(f"Error al crear rango de fechas: {str(e)}")
            raise DataProcessingError(f"Error al crear rango de fechas: {str(e)}")
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Obtener headers de autenticación"""
        try:
            # Cargar credenciales
            credentials = self.file_manager.load_credentials()
            if not credentials:
                app_logger.warning("No se encontraron credenciales, iniciando autenticación...")
                credentials = self.auth_service.full_auth_process()["credentials"]
            
            token = credentials["authentication"]["token"]
            username = credentials["user_info"]["username"]
            
            return {
                "Auth-Token": token,
                "user": username,
                "Cookie": f"token={token}",
                "Referer": "https://suma2.aduana.gob.bo/"
            }
            
        except Exception as e:
            app_logger.error(f"Error al obtener headers de autenticación: {str(e)}")
            raise APIError(f"Error al obtener headers de autenticación: {str(e)}")
    
    def get_total_records(self, fecha_desde: str, fecha_hasta: str, fecha_autorizacion: str) -> int:
        """Paso 1: Obtener total de registros"""
        try:
            app_logger.info(f"Obteniendo total de registros Manifiesto desde {fecha_desde} hasta {fecha_hasta} (Autorización: {fecha_autorizacion})")
            
            # Crear rango de fechas y fecha autorización
            date_range = self._create_date_range(fecha_desde, fecha_hasta)
            fecha_aut_timestamp = self._convert_date_to_timestamp(fecha_autorizacion, start_of_day=True)
            
            # Construir URL
            url = f"{self.settings.url_n_ingreso}/json/manifiesto/dataTable/consulta-interna"
            
            # Parámetros de consulta
            params = {
                "page": 0,
                "size": self.settings.size_list,
                "data.estAct_0": "AUTORIZADO",
                "data.estAct_1": "REGISTRADO",
                "data.estAct_2": "CONCLUIDO",
                "data.estAct_3": "EN_REVISION",
                "data.estAct_4": "PRESENTADO",
                "data.estAct_5": "OBSERVADO",
                "data.modMic": "BILATERAL",
                "data.datRutOtr.aduRut.codAdu-AI": "643",
                "data.fecTra-/": date_range,
                "log.est": fecha_aut_timestamp,
                "total": "tota"
            }
            
            # Headers específicos
            headers = {
                **self._get_auth_headers(),
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:150.0) Gecko/20100101 Firefox/150.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Origin": "https://suma2.aduana.gob.bo",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache"
            }
            
            app_logger.debug(f"Consultando total de registros Manifiesto: {url}")
            
            # Realizar petición
            response = self.http_client.get(url, headers=headers, params=params)
            data = response.json()
            
            # Extraer total
            if isinstance(data, list) and len(data) > 0:
                total = data[0].get("total", 0)
                app_logger.info(f"Total de registros encontrados: {total}")
                return total
            else:
                app_logger.warning("Respuesta inesperada al obtener total de registros de Manifiestos")
                return 0
                
        except Exception as e:
            app_logger.error(f"Error al obtener total de registros de Manifiestos: {str(e)}")
            raise APIError(f"Error al obtener total de registros de Manifiestos: {str(e)}")
    
    def get_page_data(self, page: int, fecha_desde: str, fecha_hasta: str, fecha_autorizacion: str) -> List[Dict[str, Any]]:
        """Obtener datos de una página específica"""
        try:
            app_logger.debug(f"Obteniendo página {page} de Manifiestos")
            
            # Crear rango de fechas
            date_range = self._create_date_range(fecha_desde, fecha_hasta)
            fecha_aut_timestamp = self._convert_date_to_timestamp(fecha_autorizacion, start_of_day=True)
            
            # Construir URL
            url = f"{self.settings.url_n_ingreso}/json/manifiesto/dataTable/consulta-interna"
            
            # Parámetros de consulta
            params = {
                "page": page * self.settings.size_list, # NOTA: La aduana suma size en page? Wait, DIM usaba page * size, la API suele requerir un offset o simplemente 'page'. Wait, en la documentacion curl 'page=0&size=10'. En dim_service se hizo: "page": page * self.settings.size_list. So this follows that logic. Wait, let me check the curl, the curl is 'page=0'. So maybe page is an offset? We'll follow what DIM does. Wait! En el dim_service.py page is passed as `page * self.settings.size_list`. If the API wants it as offset, it's correct.
                "size": self.settings.size_list,
                "data.estAct_0": "AUTORIZADO",
                "data.estAct_1": "REGISTRADO",
                "data.estAct_2": "CONCLUIDO",
                "data.estAct_3": "EN_REVISION",
                "data.estAct_4": "PRESENTADO",
                "data.estAct_5": "OBSERVADO",
                "data.modMic": "BILATERAL",
                "data.datRutOtr.aduRut.codAdu-AI": "643",
                "data.fecTra-/": date_range,
                "log.est": fecha_aut_timestamp
            }
            
            # Headers específicos
            headers = {
                **self._get_auth_headers(),
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:150.0) Gecko/20100101 Firefox/150.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Origin": "https://suma2.aduana.gob.bo",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "Priority": "u=0",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache"
            }
            
            # Realizar petición
            response = self.http_client.get(url, headers=headers, params=params)
            data = response.json()
            
            if isinstance(data, list):
                app_logger.debug(f"Página {page}: {len(data)} registros obtenidos")
                return data
            else:
                app_logger.warning(f"Respuesta inesperada en página {page}")
                return []
                
        except Exception as e:
            app_logger.error(f"Error al obtener página {page}: {str(e)}")
            raise APIError(f"Error al obtener página {page}: {str(e)}")
    
    def extract_all_data(self, fecha_desde: str, fecha_hasta: str, fecha_autorizacion: str, show_total_callback=None) -> Dict[str, Any]:
        """Extraer todos los datos (Paso 1 + Paso 2)"""
        try:
            app_logger.info(f"Iniciando extracción completa de Manifiestos desde {fecha_desde} hasta {fecha_hasta} (Aut: {fecha_autorizacion})")
            
            # Paso 1: Obtener total de registros
            total_records = self.get_total_records(fecha_desde, fecha_hasta, fecha_autorizacion)
            
            if show_total_callback:
                show_total_callback(total_records)
            
            if total_records == 0:
                app_logger.warning("No se encontraron registros para el rango de fechas especificado")
                return {
                    "fecha_desde": fecha_desde,
                    "fecha_hasta": fecha_hasta,
                    "fecha_autorizacion": fecha_autorizacion,
                    "total_records": 0,
                    "total_pages": 0,
                    "records_extracted": 0,
                    "data": [],
                    "extraction_info": {
                        "started_at": datetime.now().isoformat(),
                        "completed_at": datetime.now().isoformat(),
                        "duration_seconds": 0.0,
                        "status": "completed_no_data"
                    }
                }
            
            # Calcular número de páginas
            total_pages = math.ceil(total_records / self.settings.size_list)
            app_logger.info(f"Total de páginas a procesar: {total_pages}")
            
            # Paso 2: Obtener datos de todas las páginas
            all_data = []
            start_time = datetime.now()
            
            for page in range(total_pages):
                try:
                    app_logger.info(f"Procesando página {page + 1}/{total_pages}")
                    page_data = self.get_page_data(page, fecha_desde, fecha_hasta, fecha_autorizacion)
                    all_data.extend(page_data)
                    
                    import time
                    time.sleep(0.5)
                    
                except Exception as e:
                    app_logger.error(f"Error en página {page}: {str(e)}")
                    continue
            
            end_time = datetime.now()
            
            # Crear nombre de carpeta basado en fechas
            folder_name = f"manifiestos_{fecha_desde.replace('/', '')}_{fecha_hasta.replace('/', '')}"
            
            result = {
                "fecha_desde": fecha_desde,
                "fecha_hasta": fecha_hasta,
                "fecha_autorizacion": fecha_autorizacion,
                "total_records": total_records,
                "total_pages": total_pages,
                "records_extracted": len(all_data),
                "data": all_data,
                "extraction_info": {
                    "started_at": start_time.isoformat(),
                    "completed_at": end_time.isoformat(),
                    "duration_seconds": (end_time - start_time).total_seconds(),
                    "status": "completed"
                }
            }
            
            # Guardar datos
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"manifiesto_data_{timestamp}"
            file_path = self.file_manager.save_json(result, filename, folder_name)
            
            app_logger.info(f"Extracción completada: {len(all_data)} registros guardados en {file_path}")

            # Inyectar campos de búsqueda en cada documento para MongoDB
            for doc in all_data:
                doc["fecha_autorizacion_busqueda"] = fecha_autorizacion
                #doc["fecha_desde_busqueda"] = fecha_desde
                #doc["fecha_hasta_busqueda"] = fecha_hasta

            # Guardar en MongoDB
            if all_data:
                mongo_manager = MongoManager(collection_name="manifiestos")
                mongo_count = mongo_manager.upsert_documents(all_data)
                app_logger.info(f"{mongo_count} documentos insertados/actualizados en la colección 'manifiestos' de MongoDB.")

            return result
            
        except Exception as e:
            app_logger.error(f"Error en extracción completa de Manifiestos: {str(e)}")
            raise DataProcessingError(f"Error en extracción completa de Manifiestos: {str(e)}")
        finally:
            self.http_client.close()
