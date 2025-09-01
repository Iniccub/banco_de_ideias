import pymongo
import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional
from bson import ObjectId

class MongoDBManager:
    def __init__(self):
        # Configuração da conexão MongoDB
        self.connection_string = self._get_connection_string()
        self.database_name = self._get_database_name()
        self.collection_name = self._get_collection_name()
        self.client = None
        self.db = None
        self.collection = None
        
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
        """Estabelece conexão com MongoDB"""
        try:
            # Adicionar timeout para evitar travamento
            self.client = pymongo.MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000,  # 5 segundos de timeout
                connectTimeoutMS=5000
            )
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            
            # Testa a conexão
            self.client.admin.command('ping')
            st.success(f"✅ Conectado ao MongoDB: {self.database_name}.{self.collection_name}")
            return True
        except Exception as e:
            st.error(f"❌ Erro ao conectar com MongoDB: {e}")
            # Garantir que as variáveis sejam None em caso de erro
            self.client = None
            self.db = None
            self.collection = None
            return False
    
    def salvar_ideia(self, ideia_data: Dict) -> Optional[str]:
        """Salva uma nova ideia no banco de dados"""
        try:
            if self.collection is None:
                st.info("🔄 Tentando conectar ao MongoDB...")
                if not self.connect():
                    st.error("❌ Não foi possível conectar ao MongoDB")
                    return None
            
            # Adiciona timestamp
            ideia_data['data_criacao'] = datetime.now()
            ideia_data['data_atualizacao'] = datetime.now()
            
            # Insere no banco
            result = self.collection.insert_one(ideia_data)
            return str(result.inserted_id)
        
        except Exception as e:
            st.error(f"Erro ao salvar ideia: {e}")
            return None
    
    def buscar_ideias(self, filtros: Dict = None) -> List[Dict]:
        """Busca ideias no banco de dados"""
        try:
            if self.collection is None:
                st.info("🔄 Tentando conectar ao MongoDB...")
                if not self.connect():
                    st.warning("⚠️ Não foi possível conectar ao MongoDB. Nenhuma ideia será exibida.")
                    return []
            
            if filtros:
                cursor = self.collection.find(filtros)
            else:
                cursor = self.collection.find()
            
            return list(cursor.sort("data_criacao", -1))
        
        except Exception as e:
            st.error(f"Erro ao buscar ideias: {e}")
            return []
    
    def atualizar_ideia(self, ideia_id: str, novos_dados: Dict) -> bool:
        """Atualiza uma ideia existente"""
        try:
            if self.collection is None:
                if not self.connect():
                    st.error("❌ Não foi possível conectar ao MongoDB")
                    return False
            
            novos_dados['data_atualizacao'] = datetime.now()
            
            result = self.collection.update_one(
                {"_id": ObjectId(ideia_id)},  # Usar ObjectId sem pymongo.
                {"$set": novos_dados}
            )
            
            return result.modified_count > 0
        
        except Exception as e:
            st.error(f"Erro ao atualizar ideia: {e}")
            return False
    
    def deletar_ideia(self, ideia_id: str) -> bool:
        """Deleta uma ideia do banco de dados"""
        try:
            if self.collection is None:
                if not self.connect():
                    st.error("❌ Não foi possível conectar ao MongoDB")
                    return False
            
            result = self.collection.delete_one({"_id": ObjectId(ideia_id)})  # Usar ObjectId sem pymongo.
            return result.deleted_count > 0
        
        except Exception as e:
            st.error(f"Erro ao deletar ideia: {e}")
            return False
    
    def contar_ideias(self) -> int:
        """Conta o total de ideias"""
        try:
            if self.collection is None:
                if not self.connect():
                    return 0
            return self.collection.count_documents({})
        except Exception as e:
            st.error(f"Erro ao contar ideias: {e}")
            return 0
    
    def obter_estatisticas(self) -> Dict:
        """Obtém estatísticas do banco de ideias"""
        try:
            if self.collection is None:
                if not self.connect():
                    return {"total_ideias": 0, "ideias_por_categoria": {}}
            
            pipeline = [
                {
                    "$group": {
                        "_id": "$categoria",
                        "count": {"$sum": 1}
                    }
                }
            ]
            
            categorias = list(self.collection.aggregate(pipeline))
            
            return {
                "total_ideias": self.contar_ideias(),
                "ideias_por_categoria": {item["_id"]: item["count"] for item in categorias}
            }
        
        except Exception as e:
            st.error(f"Erro ao obter estatísticas: {e}")
            return {"total_ideias": 0, "ideias_por_categoria": {}}

    def testar_conexao(self) -> bool:
        """Testa a conexão com MongoDB sem salvar no Streamlit"""
        try:
            if self.collection is None:
                return self.connect()
            
            # Testa se a conexão ainda está ativa
            self.client.admin.command('ping')
            return True
        except Exception:
            return False

# Instância global do gerenciador
mongo_manager = MongoDBManager()

# Teste de conexão na inicialização (opcional)
if __name__ == "__main__":
    print("Testando conexão MongoDB...")
    if mongo_manager.testar_conexao():
        print("✅ Conexão bem-sucedida!")
    else:
        print("❌ Falha na conexão!")
    
    def buscar_ideia_por_id(self, ideia_id: str) -> Optional[Dict]:
        """Busca uma ideia específica pelo ID"""
        try:
            if self.collection is None:
                if not self.connect():
                    return None
            
            return self.collection.find_one({"_id": ObjectId(ideia_id)})
        
        except Exception as e:
            st.error(f"Erro ao buscar ideia: {e}")