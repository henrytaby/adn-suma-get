from pymongo import MongoClient
import pandas as pd
from datetime import datetime, time

# Conexión a MongoDB (ajusta si tu URI es diferente)
client = MongoClient("mongodb://localhost:27017")

# Base de datos y colección
db = client["suma"]
collection = db["dim-pisoss"]


def _convert_date_to_timestamp(date_str: str, start_of_day: bool = True) -> int:
    """Convertir fecha DD/MM/YYYY a timestamp"""
    date_obj = datetime.strptime(date_str, "%d/%m/%Y")
    if start_of_day:
        date_obj = date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        date_obj = date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
    timestamp_seconds = int(date_obj.timestamp())
    timestamp = timestamp_seconds * 1000
    return timestamp

def _convert_timestamp_to_str(timestamp: int) -> str:
    """Convierte un timestamp en milisegundos a string 'dd/mm/yyyy HH:MM:SS'"""
    dt = datetime.fromtimestamp(timestamp // 1000)
    return dt.strftime("%d/%m/%Y %H:%M:%S")

# Timestamps de búsqueda
start_timestamp = _convert_date_to_timestamp(date_str="20/04/2026", start_of_day=True)
end_timestamp = _convert_date_to_timestamp(date_str="23/04/2026", start_of_day=False)
print(f"Fecha inicio : {start_timestamp}")
print(f"Fecha Fin : {end_timestamp}")

# Consulta
query = {
    "fecTra": {
        "$gte": start_timestamp,
        "$lte": end_timestamp
    }
}

# Campos a proyectar
projection = {
    "_id": 0,
    "num": 1,
    "fecTra": 1,
    "sel.can": 1,
    "estAct": 1,
    "fecEstAct": 1,
    "numRef": 1,
    "desDesRegAdu": 1,
    "desModReg": 1,
    "desModDep": 1,
    "dec.nomRazSoc": 1,
    "imp.nomRazSoc": 1,
    "nomRazSoc": 1,
    "lug.desPaiPro": 1,
    "totConDec.totFob": 1,
    "totConDec.totPesBru": 1,
    "pro": 1,
    "desAduDep": 1
    
}

# Ejecutar consulta y ordenar por fecTra ascendente
cursor = collection.find(query, projection).sort("fecTra", 1)

# Convertir a lista de documentos
data = list(cursor)

# Convertir a DataFrame
if data:
    # Normalizar los datos anidados
    df = pd.json_normalize(data)

    print(df.columns)

    # Crear columna 'Fecha y Hora de Registro' a partir de 'fecTra'
    df['Fecha y Hora de Registro'] = df['fecTra'].apply(_convert_timestamp_to_str)

    if 'pro' in df.columns:
        print("Ejemplo de df['pro']:", df['pro'].head(5).tolist())
    else:
        print("No existe la columna 'pro' en el DataFrame")

    # Extraer 'nomRazSoc' del primer elemento de 'pro', o dejar vacío si no existe
    def extraer_nomrazsoc(pro):
        if isinstance(pro, list) and len(pro) > 0 and isinstance(pro[0], dict):
            return pro[0].get('nomRazSoc', '')
        return ''

    if 'pro' in df.columns:
        df['nomRazSoc'] = df['pro'].apply(extraer_nomrazsoc)

    if 'nomRazSoc' in df.columns:
        print("Primeros valores de 'nomRazSoc':", df['nomRazSoc'].head(5).tolist())
    else:
        print("No existe la columna 'nomRazSoc' en el DataFrame")

    # Asegurar que 'Proveedor' (nomRazSoc) exista, si no, dejar vacío
    if 'nomRazSoc' not in df.columns:
        df['nomRazSoc'] = ""

    # Renombrar columnas según tu requerimiento
    df_final = df.rename(columns={
        'num': 'N° de la Declaración',
        'Fecha y Hora de Registro': 'Fecha y Hora de Registro',
        'sel.can': 'Canal',
        'estAct': 'Estado',
        'desDesRegAdu': 'Destino/Régimen Aduanero',
        'desModReg': 'Modalidad Régimen',
        'desModDep': 'Modalidad de despacho',
        'dec.nomRazSoc': 'Despachante',
        'imp.nomRazSoc': 'Importador',
        'nomRazSoc': 'Proveedor',
        'lug.desPaiPro': 'País Procedencia',
        'totConDec.totFob': 'Valor FOB (USD)',
        'totConDec.totPesBru': 'Peso Bruto (KG)',
        'desAduDep': 'Aduana Departamento',
    })

    # Seleccionar y ordenar las columnas en el orden deseado
    columnas_orden = [
        'N° de la Declaración',
        'Fecha y Hora de Registro',
        'Canal',
        'Estado',
        'Destino/Régimen Aduanero',
        'Modalidad Régimen',
        'Modalidad de despacho',
        'Despachante',
        'Importador',
        'Proveedor',
        'País Procedencia',
        'Valor FOB (USD)',
        'Peso Bruto (KG)',
        'Aduana Departamento'
    ]

    # Asegurar que todas las columnas existan, aunque sea vacías
    for col in columnas_orden:
        if col not in df_final.columns:
            df_final[col] = ""
    df_final = df_final[columnas_orden]

    # Convertir todo a texto
    for col in df_final.columns:
        df_final[col] = df_final[col].astype(str)

    # Exportar a Excel
    df_final.to_excel("dim_reporte.xlsx", index=False, engine='openpyxl')
    print(f"Exportados {len(df_final)} registros a 'dim_reporte.xlsx'")
else:
    print("No se encontraron registros para exportar.")