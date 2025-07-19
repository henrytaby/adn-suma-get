"""
Servicio para extracción de datos DIM (Ingreso de Mercancías)
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

class DIMService:
    """Servicio para extracción de datos DIM"""
    
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
                # 00:00:00 para fecha inicio
                date_obj = date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                # 23:59:59 para fecha fin
                #date_obj = date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
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
                "Referer": "https://suma.aduana.gob.bo/ingreso/consulta/"
            }
            
        except Exception as e:
            app_logger.error(f"Error al obtener headers de autenticación: {str(e)}")
            raise APIError(f"Error al obtener headers de autenticación: {str(e)}")
    
    def get_total_records(self, fecha_desde: str, fecha_hasta: str) -> int:
        """Paso 1: Obtener total de registros"""
        try:
            app_logger.info(f"Obteniendo total de registros DIM desde {fecha_desde} hasta {fecha_hasta}")
            
            # Crear rango de fechas
            date_range = self._create_date_range(fecha_desde, fecha_hasta)
            
            # Construir URL
            url = f"{self.settings.url_n_ingreso}/json/dim/dataTable/consulta-interna"
            
            # Parámetros de consulta
            params = {
                "page": 0,
                "size": self.settings.size_list,
                "data.estAct_0": "REGISTRADO",
                "data.estAct_1": "OBSERVADO",
                "data.estAct_2": "CONCLUIDO",
                "data.estAct_3": "ANULADO",
                "data.estAct_4": "ACEPTADA",
                "data.estAct_5": "PAGADA",
                "data.estAct_6": "LEVANTE",
                "data.estAct_7": "EN_ABANDONO",
                "data.estAct_8": "EN_ABANDONO_CONFIRMADO",
                "data.estAct_9": "POR_REGULARIZAR",
                "data.estAct_10": "POR_REGULARIZAR_VENCIDO",
                "data.estAct_11": "EN_AFORO",
                "data.estAct_12": "CON_CANAL_ASIGNADO",
                "data.estAct_13": "REGULARIZADO",
                "data.fecTra-/": date_range,
                "total": "tota"
            }
            
            # Headers específicos para DIM
            headers = {
                **self._get_auth_headers(),
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache"
            }
            
            app_logger.debug(f"Consultando total de registros: {url}")
            
            # Realizar petición
            response = self.http_client.get(url, headers=headers, params=params)
            
            # Mostrar en pantalla la URL y headers para comparar con Postman
            print("\n--- PETICIÓN PASO 1 (TOTAL REGISTROS) ---")
            print("URL:", response.request.url)
            print("HEADERS:")
            for k, v in headers.items():
                print(f"  {k}: {v}")
            print("PARAMS:")
            for k, v in params.items():
                print(f"  {k}: {v}")
            print("RESPUESTA:")
            print(f"Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")
            print("----------------------------------------\n")
            data = response.json()
            
            # Extraer total
            if isinstance(data, list) and len(data) > 0:
                total = data[0].get("total", 0)
                app_logger.info(f"Total de registros encontrados: {total}")
                return total
            else:
                app_logger.warning("Respuesta inesperada al obtener total de registros")
                return 0
                
        except Exception as e:
            app_logger.error(f"Error al obtener total de registros: {str(e)}")
            raise APIError(f"Error al obtener total de registros: {str(e)}")
    
    def get_page_data(self, page: int, fecha_desde: str, fecha_hasta: str) -> List[Dict[str, Any]]:
        """Obtener datos de una página específica"""
        try:
            app_logger.debug(f"Obteniendo página {page}")
            
            # Crear rango de fechas
            date_range = self._create_date_range(fecha_desde, fecha_hasta)
            
            # Construir URL
            url = f"{self.settings.url_n_ingreso}/json/dim/dataTable/consulta-interna"
            
            # Parámetros de consulta
            params = {
                "page": page * self.settings.size_list,
                "size": self.settings.size_list,
                "data.estAct_0": "REGISTRADO",
                "data.estAct_1": "OBSERVADO",
                "data.estAct_2": "CONCLUIDO",
                "data.estAct_3": "ANULADO",
                "data.estAct_4": "ACEPTADA",
                "data.estAct_5": "PAGADA",
                "data.estAct_6": "LEVANTE",
                "data.estAct_7": "EN_ABANDONO",
                "data.estAct_8": "EN_ABANDONO_CONFIRMADO",
                "data.estAct_9": "POR_REGULARIZAR",
                "data.estAct_10": "POR_REGULARIZAR_VENCIDO",
                "data.estAct_11": "EN_AFORO",
                "data.estAct_12": "CON_CANAL_ASIGNADO",
                "data.estAct_13": "REGULARIZADO",
                "data.fecTra-/": date_range
            }
            
            # Headers específicos para DIM
            headers = {
                **self._get_auth_headers(),
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
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
    
    def extract_all_dim_data(self, fecha_desde: str, fecha_hasta: str, show_total_callback=None) -> Dict[str, Any]:
        """Extraer todos los datos DIM (Paso 1 + Paso 2)"""
        try:
            app_logger.info(f"Iniciando extracción completa de datos DIM desde {fecha_desde} hasta {fecha_hasta}")
            
            # Paso 1: Obtener total de registros
            total_records = self.get_total_records(fecha_desde, fecha_hasta)
            
            # Mostrar el total en CLI si se pasa un callback
            if show_total_callback:
                show_total_callback(total_records)
            
            if total_records == 0:
                app_logger.warning("No se encontraron registros para el rango de fechas especificado")
                return {
                    "fecha_desde": fecha_desde,
                    "fecha_hasta": fecha_hasta,
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
                    page_data = self.get_page_data(page, fecha_desde, fecha_hasta)
                    all_data.extend(page_data)
                    
                    # Pequeña pausa para no sobrecargar el servidor
                    import time
                    time.sleep(0.5)
                    
                except Exception as e:
                    app_logger.error(f"Error en página {page}: {str(e)}")
                    # Continuar con la siguiente página
                    continue
            
            end_time = datetime.now()
            
            # Crear nombre de carpeta basado en fechas
            folder_name = f"dim_{fecha_desde.replace('/', '')}_{fecha_hasta.replace('/', '')}"
            
            # Preparar resultado final
            result = {
                "fecha_desde": fecha_desde,
                "fecha_hasta": fecha_hasta,
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
            filename = f"dim_data_{timestamp}"
            file_path = self.file_manager.save_json(result, filename, folder_name)
            
            app_logger.info(f"Extracción completada: {len(all_data)} registros guardados en {file_path}")

            # Guardar en MongoDB
            if all_data:
                mongo_manager = MongoManager()
                mongo_count = mongo_manager.upsert_documents(all_data)
                app_logger.info(f"{mongo_count} documentos insertados/actualizados en MongoDB.")

            return result
            
        except Exception as e:
            app_logger.error(f"Error en extracción completa de datos DIM: {str(e)}")
            raise DataProcessingError(f"Error en extracción completa de datos DIM: {str(e)}")
        finally:
            # Cerrar cliente HTTP
            self.http_client.close() 