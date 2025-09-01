import pymongo
import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional
from bson import ObjectId

class MongoDBManager:
    def __init__(self):
        # Não inicializa as credenciais no __init__
        self.connection_string = None
        self.database_name = None
        self.collection_name = None
        self.client = None
        self.db = None
        self.collection = None
        self._initialized = False
        
    def _initialize(self):
        """Inicializa as configurações apenas quando necessário"""
        if not self._initialized:
            self.connection_string = self._get_connection_string()
            self.database_name = self._get_database_name()
            self.collection_name = self._get_collection_name()
            self._initialized = True
        
    def _get_connection_string(self) -> str:
        """Obtém a string de conexão do MongoDB dos segredos do Streamlit"""
        try:
            # Busca as credenciais dos segredos do Streamlit
            username = st.secrets["mongodb"]["username"]
            password = st.secrets["mongodb"]["password"]
            cluster_url = st.secrets["mongodb"]["cluster_url"]
            
            # Constrói a string de conexão
            connection_string = f"mongodb+srv://{username}:{password}@{cluster_url}/?retryWrites=true&w=majority"
            return connection_string
            
        except KeyError as e:
            st.error(f"❌ Credencial MongoDB não encontrada nos segredos do Streamlit: {e}")
            st.error("❌ Verifique se as credenciais estão configuradas em .streamlit/secrets.toml")
            raise ValueError(f"Credenciais MongoDB não configuradas: {e}")
        except Exception as e:
            st.error(f"❌ Erro ao obter credenciais do MongoDB: {e}")
            raise ValueError(f"Erro nas credenciais MongoDB: {e}")
    
    def _get_database_name(self) -> str:
        """Obtém o nome do banco de dados dos segredos do Streamlit"""
        try:
            return st.secrets["mongodb"].get("database_name", "ideias")
        except KeyError:
            st.warning("⚠️ Nome do banco não encontrado nos segredos, usando padrão: 'ideias'")
            return "ideias"
    
    def _get_collection_name(self) -> str:
        """Obtém o nome da coleção dos segredos do Streamlit"""
        try:
            return st.secrets["mongodb"].get("collection_name", "banco_ideias")
        except KeyError:
            st.warning("⚠️ Nome da coleção não encontrado nos segredos, usando padrão: 'banco_ideias'")
            return "banco_ideias"
    
    def connect(self) -> bool:
        """Conecta ao MongoDB"""
        try:
            # Inicializa as configurações se necessário
            self._initialize()
            
            if self.client is None:
                self.client = pymongo.MongoClient(self.connection_string)
                self.db = self.client[self.database_name]
                self.collection = self.db[self.collection_name]
            
            # Testa a conexão
            self.client.admin.command('ping')
            return True
            
        except Exception as e:
            st.error(f"❌ Erro ao conectar ao MongoDB: {e}")
            return False
    
    def salvar_ideia(self, ideia_data: Dict) -> Optional[str]:
        """Salva uma nova ideia no MongoDB"""
        try:
            if self.collection is None:
                if not self.connect():
                    return None
            
            # Adiciona timestamp se não existir
            if 'data_criacao' not in ideia_data:
                ideia_data['data_criacao'] = datetime.now()
            
            # Insere o documento
            resultado = self.collection.insert_one(ideia_data)
            return str(resultado.inserted_id)
            
        except Exception as e:
            st.error(f"❌ Erro ao salvar ideia: {e}")
            return None
    
    def buscar_ideias(self, filtros: Dict = None) -> List[Dict]:
        """Busca ideias no MongoDB com filtros opcionais"""
        try:
            if self.collection is None:
                if not self.connect():
                    return []
            
            if filtros is None:
                filtros = {}
            
            # Busca os documentos
            cursor = self.collection.find(filtros).sort("data_criacao", -1)
            ideias = list(cursor)
            
            # Converte ObjectId para string para compatibilidade
            for ideia in ideias:
                if '_id' in ideia:
                    ideia['_id'] = str(ideia['_id'])
            
            return ideias
            
        except Exception as e:
            st.error(f"❌ Erro ao buscar ideias: {e}")
            return []
    
    def atualizar_ideia(self, ideia_id: str, novos_dados: Dict) -> bool:
        """Atualiza uma ideia existente"""
        try:
            if self.collection is None:
                if not self.connect():
                    return False
            
            # Adiciona timestamp de atualização
            novos_dados['data_atualizacao'] = datetime.now()
            
            # Atualiza o documento
            resultado = self.collection.update_one(
                {"_id": ObjectId(ideia_id)},
                {"$set": novos_dados}
            )
            
            return resultado.modified_count > 0
            
        except Exception as e:
            st.error(f"❌ Erro ao atualizar ideia: {e}")
            return False
    
    def deletar_ideia(self, ideia_id: str) -> bool:
        """Deleta uma ideia"""
        try:
            if self.collection is None:
                if not self.connect():
                    return False
            
            resultado = self.collection.delete_one({"_id": ObjectId(ideia_id)})
            return resultado.deleted_count > 0
            
        except Exception as e:
            st.error(f"❌ Erro ao deletar ideia: {e}")
            return False
    
    def contar_ideias(self) -> int:
        """Conta o total de ideias"""
        try:
            if self.collection is None:
                if not self.connect():
                    return 0
            
            return self.collection.count_documents({})
            
        except Exception as e:
            st.error(f"❌ Erro ao contar ideias: {e}")
            return 0
    
    def obter_estatisticas(self) -> Dict:
        """Obtém estatísticas das ideias"""
        try:
            if self.collection is None:
                if not self.connect():
                    return {}
            
            pipeline = [
                {
                    "$group": {
                        "_id": "$categoria",
                        "total": {"$sum": 1}
                    }
                }
            ]
            
            resultado = list(self.collection.aggregate(pipeline))
            return {item["_id"]: item["total"] for item in resultado}
            
        except Exception as e:
            st.error(f"❌ Erro ao obter estatísticas: {e}")
            return {}
    
    def testar_conexao(self) -> bool:
        """Testa a conexão com o MongoDB"""
        try:
            return self.connect()
        except Exception:
            return False
    
    def buscar_ideia_por_id(self, ideia_id: str) -> Optional[Dict]:
        """Busca uma ideia específica pelo ID"""
        try:
            if self.collection is None:
                if not self.connect():
                    return None
            
            ideia = self.collection.find_one({"_id": ObjectId(ideia_id)})
            if ideia and '_id' in ideia:
                ideia['_id'] = str(ideia['_id'])
            return ideia
        
        except Exception as e:
            st.error(f"Erro ao buscar ideia: {e}")
            return None

# Função para obter a instância do gerenciador (lazy loading)
def get_mongo_manager():
    """Retorna a instância do MongoDB Manager"""
    global _mongo_manager_instance
    if '_mongo_manager_instance' not in globals():
        _mongo_manager_instance = MongoDBManager()
    return _mongo_manager_instance

# Para compatibilidade com código existente
mongo_manager = get_mongo_manager()

# Teste de conexão apenas quando executado diretamente
if __name__ == "__main__":
    print("Testando conexão MongoDB...")
    manager = MongoDBManager()
    if manager.testar_conexao():
        print("✅ Conexão bem-sucedida!")
    else:
        print("❌ Falha na conexão!")