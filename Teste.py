# No terminal Python ou em um script de teste
from mongodb_connection import mongo_manager

# Testa a conexão
if mongo_manager.connect():
    print("✅ Conexão com MongoDB estabelecida!")
    print(f"Database: {mongo_manager.database_name}")
    print(f"Collection: {mongo_manager.collection_name}")
else:
    print("❌ Falha na conexão com MongoDB")