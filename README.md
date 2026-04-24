# ADN Suma Get - Sistema de Extracción de Datos

Sistema robusto y escalable para extraer datos del sistema web de aduanas, diseñado siguiendo los principios SOLID y las mejores prácticas de desarrollo.

## 🚀 Características

- **Arquitectura orientada a objetos** siguiendo principios SOLID
- **Gestión de configuración** mediante variables de entorno
- **Sistema de autenticación** completo con JWT
- **Manejo robusto de errores** y reintentos automáticos
- **Logging detallado** con rotación de archivos
- **CLI intuitivo** para ejecutar diferentes operaciones
- **Almacenamiento organizado** de datos por módulo y fecha
- **Escalabilidad** para múltiples endpoints

## 📋 Requisitos

- Python 3.8+
- Dependencias listadas en `requirements.txt`

## 🛠️ Instalación

1. **Clonar el repositorio:**
```bash
git clone <repository-url>
cd adn-suma-get
```

2. **Crear entorno virtual:**
```bash
python -m venv venv
```

3. **Activar entorno virtual:**
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

5. **Configurar variables de entorno:**
```bash
# Copiar el archivo de ejemplo y configurar
cp config.env.example config.env
# Editar config.env con tus credenciales y configuración
```

## ⚙️ Configuración

### Archivo de configuración

El proyecto incluye un archivo de ejemplo `config.env.example` que contiene todas las variables necesarias sin valores sensibles. Para configurar el sistema:

1. **Copiar el archivo de ejemplo:**
```bash
cp config.env.example config.env
```

2. **Editar `config.env` con tus valores:**

```env
# Configuración de autenticación
NOMBRE_USUARIO=tu_usuario
PASSWORD=tu_password
URL_B_SSO=https://suma.aduana.gob.bo/b-sso/rest
SIZE_LIST=100

# Configuración de la aplicación
DEBUG=true
LOG_LEVEL=INFO
OUTPUT_DIR=output
CREDENTIALS_FILE=credenciales.json
VERIFY_FILE=verificar.json

# Configuración de requests
REQUEST_TIMEOUT=30
MAX_RETRIES=3
RETRY_DELAY=1
```

## 🎯 Uso

### Comandos principales

**Ejecutar autenticación completa:**
```bash
python main.py auth
```

**Ejecutar paso específico:**
```bash
# Solo autenticación
python main.py auth --step 1

# Solo credenciales
python main.py auth --step 2

# Solo verificación
python main.py auth --step 3
```

**Forzar nueva autenticación:**
```bash
python main.py auth --force
```

**Verificar estado de autenticación:**
```bash
python main.py status
```

**Mostrar información del sistema:**
```bash
python main.py info
```

**Extraer datos DIM (Ingreso de Mercancías):**
```bash
# Extracción básica
python main.py dim --fecha-desde 01/04/2025 --fecha-hasta 30/04/2025

# Con nueva autenticación
python main.py dim --fecha-desde 01/04/2025 --fecha-hasta 30/04/2025 --force-auth
```

**Extraer datos de Manifiestos de Carga:**
```bash
# Extracción de manifiestos con fechas y fecha de autorización
python main.py manifiesto --fecha-desde 20/03/2026 --fecha-hasta 20/04/2026 --fecha-autorizacion 20/04/2026

# Con nueva autenticación
python main.py manifiesto --fecha-desde 20/03/2026 --fecha-hasta 20/04/2026 --fecha-autorizacion 20/04/2026 --force-auth
```

### Estructura de archivos generados

```
output/
├── auth/
│   └── 2024-01-15/
│       ├── authentication_response_143022.json
│       ├── credentials_response_143025.json
│       └── verify_response_143028.json
├── dim_01042025_30042025/
│   └── 2024-01-15/
│       └── dim_data_20240115_143022.json
├── manifiestos_20032026_20042026/
│   └── 2024-01-15/
│       └── manifiesto_data_20240115_143022.json
├── credenciales.json
└── verificar.json
```

## 🏗️ Arquitectura

### Estructura del proyecto

```
adn-suma-get/
├── app/
│   ├── config/          # Configuración del sistema
│   ├── core/            # Funcionalidades base
│   ├── services/        # Servicios de negocio
│   └── cli/             # Comandos de línea de comandos
├── logs/                # Archivos de log
├── output/              # Datos extraídos
├── config.env           # Variables de entorno
├── requirements.txt     # Dependencias
├── main.py             # Punto de entrada
└── README.md           # Documentación
```

### Principios SOLID aplicados

- **S**: Cada clase tiene una responsabilidad única
- **O**: Extensible para nuevos endpoints sin modificar código existente
- **L**: Las clases derivadas pueden sustituir a las base
- **I**: Interfaces específicas para cada funcionalidad
- **D**: Dependencia de abstracciones, no de implementaciones

## 🔧 Desarrollo

### Agregar nuevo endpoint

1. Crear nuevo servicio en `app/services/`
2. Implementar lógica de extracción
3. Agregar comando CLI en `app/cli/commands.py`
4. Configurar variables de entorno si es necesario

### Logging

El sistema utiliza `loguru` para logging con:
- Salida a consola con colores
- Archivos de log con rotación diaria
- Retención de 30 días
- Compresión automática

## 📝 Licencia

Este proyecto es privado y confidencial.

## 🤝 Contribución

Para contribuir al proyecto:
1. Crear rama feature
2. Implementar cambios
3. Ejecutar pruebas
4. Crear pull request

## 📞 Soporte

Para soporte técnico, contactar al equipo de desarrollo. 