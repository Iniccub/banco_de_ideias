
import streamlit as st
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.files.file import File

class SharePoint:
    def __init__(self):
        """Inicializa a classe e obtém as credenciais do st.secrets"""
        self._load_credentials()
    
    def _load_credentials(self):
        """Carrega as credenciais do SharePoint dos segredos do Streamlit"""
        try:
            # Busca as credenciais da seção [sharepoint] do TOML
            self.username = st.secrets["sharepoint"]["sharepoint_email"]
            self.password = st.secrets["sharepoint"]["sharepoint_password"]
            self.sharepoint_site = st.secrets["sharepoint"]["sharepoint_url_site"]
            self.sharepoint_site_name = st.secrets["sharepoint"]["sharepoint_site_name"]
            self.sharepoint_doc = st.secrets["sharepoint"]["sharepoint_doc_library"]
            
            # Valida se todas as credenciais foram fornecidas
            if not all([self.username, self.password, self.sharepoint_site, 
                       self.sharepoint_site_name, self.sharepoint_doc]):
                raise ValueError("Uma ou mais credenciais do SharePoint estão vazias")
                
        except KeyError as e:
            st.error(f"❌ Credencial do SharePoint não encontrada no st.secrets: {e}")
            st.error("❌ Verifique se as credenciais estão configuradas em .streamlit/secrets.toml")
            st.error("❌ Certifique-se de que as credenciais estão na seção [sharepoint]")
            raise ValueError(f"Credencial do SharePoint não encontrada: {e}")
        except Exception as e:
            st.error(f"❌ Erro ao carregar credenciais do SharePoint: {e}")
            raise ValueError(f"Erro nas credenciais do SharePoint: {e}")

    def _auth(self):
        """Autentica no SharePoint"""
        try:
            conn = ClientContext(self.sharepoint_site).with_credentials(
                UserCredential(
                    self.username,
                    self.password
                )
            )
            return conn
        except Exception as e:
            st.error(f"❌ Erro na autenticação do SharePoint: {e}")
            raise

    def _get_files_list(self, folder_name):
        """Obtém lista de arquivos de uma pasta"""
        conn = self._auth()
        target_folder_url = f'/sites/{self.sharepoint_site_name}/{self.sharepoint_doc}/{folder_name}'
        root_folder = conn.web.get_folder_by_server_relative_url(target_folder_url)
        root_folder.expand(['Files', 'Folders']).get().execute_query()
        return root_folder.files

    def download_file(self, file_name, folder_name):
        """Baixa um arquivo do SharePoint"""
        try:
            conn = self._auth()
            file_url = f'/sites/{self.sharepoint_site_name}/{self.sharepoint_doc}/{folder_name}/{file_name}'
            file = File.open_binary(conn, file_url)
            return file.content
        except Exception as e:
            st.error(f"❌ Erro ao baixar arquivo {file_name}: {str(e)}")
            raise Exception(f"Erro ao baixar arquivo {file_name}: {str(e)}")

    def upload_file(self, file_name, folder_name, content):
        """Faz upload de um arquivo para o SharePoint"""
        try:
            conn = self._auth()
            target_folder_url = f'/sites/{sharepoint_site_name}/{sharepoint_doc}/{folder_name}'
            target_folder = conn.web.get_folder_by_server_relative_path(target_folder_url)
            response = target_folder.upload_file(file_name, content).execute_query()
            return response
        except Exception as e:
            raise Exception(f"Erro ao fazer upload do arquivo {file_name}: {str(e)}")

    def test_connection(self):
        """Testa a conexão com o SharePoint com diagnóstico detalhado"""
        try:
            conn = self._auth()
            
            # Teste 1: Acessar informações do site
            web = conn.web.get().execute_query()
            
            # Teste 2: Verificar biblioteca específica
            target_lib = conn.web.lists.get_by_title(sharepoint_doc)
            target_lib.get().execute_query()
            
            return True, f"Conexão bem-sucedida com: {web.title}"
            
        except Exception as e:
            error_msg = str(e)
            
            # Diagnóstico específico
            if "401" in error_msg or "Unauthorized" in error_msg:
                return False, "Erro 401: Credenciais inválidas ou autenticação básica desabilitada"
            elif "403" in error_msg or "Forbidden" in error_msg:
                return False, "Erro 403: Usuário não tem permissão para acessar o site"
            elif "404" in error_msg or "Not Found" in error_msg:
                return False, "Erro 404: Site ou biblioteca não encontrada"
            elif "timeout" in error_msg.lower():
                return False, "Erro de timeout: Verifique a conectividade de rede"
            else:
                return False, f"Erro de conexão: {error_msg}"

# Exportar a classe SharePoint
__all__ = ['SharePoint']