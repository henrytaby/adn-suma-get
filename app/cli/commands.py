"""
Comandos CLI para el sistema ADN
"""
import click
from app.services.auth_service import AuthService
from app.core.logger import app_logger
from app.core.exceptions import AuthenticationError

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
    click.echo(f"  Usuario: {settings.nombre_usuario}")
    click.echo(f"  Directorio de salida: {settings.output_dir}")
    click.echo(f"  Archivo de credenciales: {settings.credentials_file}")
    click.echo(f"  Archivo de verificación: {settings.verify_file}")
    click.echo(f"  Timeout de requests: {settings.request_timeout}s")
    click.echo(f"  Reintentos máximos: {settings.max_retries}")

if __name__ == '__main__':
    cli() 