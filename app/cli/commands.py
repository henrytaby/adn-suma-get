"""
Comandos CLI para el sistema ADN
"""
import click
from app.services.auth_service import AuthService
from app.services.dim_service import DIMService
from app.core.logger import app_logger
from app.core.exceptions import AuthenticationError, DataProcessingError

@click.group()
def cli():
    """Sistema de extracción de datos ADN Suma Get"""
    pass

@cli.command()
@click.option('--step', type=click.Choice(['1', '2', '3', 'all']), default='all',
              help='Paso específico a ejecutar (1: autenticación, 2: credenciales, 3: verificación, all: todos)')
@click.option('--force', is_flag=True, help='Forzar nueva autenticación aunque existan credenciales')
def auth(step, force):
    """Ejecutar proceso de autenticación"""
    try:
        auth_service = AuthService()
        
        if step == 'all':
            if force or not auth_service.check_auth_status():
                app_logger.info("Ejecutando proceso completo de autenticación...")
                result = auth_service.full_auth_process()
                click.echo("✅ Proceso de autenticación completado exitosamente")
                click.echo(f"Usuario: {result['credentials']['user_info']['username']}")
                click.echo(f"Roles: {', '.join(result['credentials']['user_info']['authorities'])}")
            else:
                click.echo("✅ Autenticación vigente, no es necesario reautenticar")
                
        elif step == '1':
            app_logger.info("Ejecutando paso 1: Autenticación...")
            credentials = auth_service.authenticate()
            click.echo("✅ Paso 1 completado: Autenticación exitosa")
            click.echo(f"Usuario: {credentials['user_info']['username']}")
            
        elif step == '2':
            app_logger.info("Ejecutando paso 2: Obtención de credenciales...")
            credentials = auth_service.get_credentials()
            click.echo("✅ Paso 2 completado: Credenciales obtenidas")
            
        elif step == '3':
            app_logger.info("Ejecutando paso 3: Verificación de token...")
            verify_data = auth_service.verify_token()
            click.echo("✅ Paso 3 completado: Token verificado")
            
    except AuthenticationError as e:
        app_logger.error(f"Error de autenticación: {str(e)}")
        click.echo(f"❌ Error de autenticación: {str(e)}")
        exit(1)
    except Exception as e:
        app_logger.error(f"Error inesperado: {str(e)}")
        click.echo(f"❌ Error inesperado: {str(e)}")
        exit(1)

@cli.command()
def status():
    """Verificar estado de autenticación"""
    try:
        auth_service = AuthService()
        
        if auth_service.check_auth_status():
            click.echo("✅ Autenticación vigente")
        else:
            click.echo("❌ Autenticación expirada o no válida")
            
    except Exception as e:
        app_logger.error(f"Error al verificar estado: {str(e)}")
        click.echo(f"❌ Error al verificar estado: {str(e)}")
        exit(1)

@cli.command()
def info():
    """Mostrar información del sistema"""
    from app.config.settings import get_settings
    
    settings = get_settings()
    
    click.echo("🔧 Configuración del sistema:")
    click.echo(f"  URL B-SSO: {settings.url_b_sso}")
    click.echo(f"  URL N-INGRESO: {settings.url_n_ingreso}")
    click.echo(f"  Usuario: {settings.nombre_usuario}")
    click.echo(f"  Directorio de salida: {settings.output_dir}")
    click.echo(f"  Archivo de credenciales: {settings.credentials_file}")
    click.echo(f"  Archivo de verificación: {settings.verify_file}")
    click.echo(f"  Timeout de requests: {settings.request_timeout}s")
    click.echo(f"  Reintentos máximos: {settings.max_retries}")

@cli.command()
@click.option('--fecha-desde', required=True, help='Fecha desde (formato: DD/MM/YYYY)')
@click.option('--fecha-hasta', required=True, help='Fecha hasta (formato: DD/MM/YYYY)')
@click.option('--force-auth', is_flag=True, help='Forzar nueva autenticación antes de extraer')
def dim(fecha_desde, fecha_hasta, force_auth):
    """Extraer datos DIM (Ingreso de Mercancías)"""
    try:
        # Verificar autenticación si es necesario
        if force_auth:
            app_logger.info("Forzando nueva autenticación...")
            auth_service = AuthService()
            auth_service.full_auth_process()
        
        # Iniciar extracción DIM
        dim_service = DIMService()
        def show_total(total):
            click.echo(f"🔎 Total de registros encontrados: {total}")
        result = dim_service.extract_all_dim_data(fecha_desde, fecha_hasta, show_total_callback=show_total)
        
        # Mostrar resultados
        click.echo("✅ Extracción DIM completada exitosamente")
        click.echo(f"📅 Rango de fechas: {result['fecha_desde']} - {result['fecha_hasta']}")
        click.echo(f"📊 Total de registros: {result['total_records']}")
        click.echo(f"📄 Total de páginas: {result['total_pages']}")
        click.echo(f"📋 Registros extraídos: {result['records_extracted']}")
        click.echo(f"⏱️  Duración: {result['extraction_info']['duration_seconds']:.2f} segundos")
        
        if result['total_records'] > 0:
            click.echo(f"💾 Datos guardados en carpeta: dim_{fecha_desde.replace('/', '')}_{fecha_hasta.replace('/', '')}")
        
    except DataProcessingError as e:
        app_logger.error(f"Error en extracción DIM: {str(e)}")
        click.echo(f"❌ Error en extracción DIM: {str(e)}")
        exit(1)
    except Exception as e:
        app_logger.error(f"Error inesperado en extracción DIM: {str(e)}")
        click.echo(f"❌ Error inesperado: {str(e)}")
        exit(1)

if __name__ == '__main__':
    cli() 