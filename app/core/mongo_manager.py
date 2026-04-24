"""
Gestor de MongoDB para operaciones básicas de inserción y actualización
"""
from pymongo import MongoClient, UpdateOne
from pymongo.errors import PyMongoError
from app.config.settings import get_settings
from app.core.logger import app_logger

class MongoManager:
    def __init__(self, collection_name=None):
        settings = get_settings()
        self.client = MongoClient(settings.mongodb_uri)
        self.db = self.client[settings.mongodb_db]
        
        # Usar la colección pasada por parámetro, si no, usar la por defecto
        col_name = collection_name if collection_name else settings.mongodb_collection
        self.collection = self.db[col_name]

    def upsert_documents(self, documents):
        """
        Inserta o actualiza documentos en la colección según el campo _id.
        Si el documento ya existe (por _id), lo actualiza; si no, lo inserta.
        """
        if not documents:
            return 0
        # Asegurar que cada documento tenga _id
        for doc in documents:
            if "id" in doc:
                doc["_id"] = doc["id"]
        operations = [
            UpdateOne({"_id": doc["_id"]}, {"$set": doc}, upsert=True)
            for doc in documents if "_id" in doc
        ]
        try:
            result = self.collection.bulk_write(operations, ordered=False)
            app_logger.info(f"MongoDB: {result.upserted_count} insertados, {result.modified_count} actualizados.")
            return result.upserted_count + result.modified_count
        except PyMongoError as e:
            app_logger.error(f"Error al guardar en MongoDB: {str(e)}")
            return 0 