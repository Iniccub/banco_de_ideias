
import streamlit as st
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.files.file import File

# Obter as credenciais do st.secrets (Streamlit Cloud)
try:
    username = st.secrets["sharepoint_email"]
    password = st.secrets["sharepoint_password"]
    sharepoint_site = st.secrets["sharepoint_url_site"]
    sharepoint_site_name = st.secrets["sharepoint_site_name"]
    sharepoint_doc = st.secrets["sharepoint_doc_library"]
except KeyError as e:
    raise ValueError(f"Credencial do SharePoint não encontrada no st.secrets: {e}")

class SharePoint:
    def __init__(self):
        """Inicializa a classe e valida as credenciais"""
        if not all([username, password, sharepoint_site, sharepoint_site_name, sharepoint_doc]):
            raise ValueError("Credenciais do SharePoint não foram configuradas corretamente no st.secrets.")
    
    def _auth(self):
        conn = ClientContext(sharepoint_site).with_credentials(
            UserCredential(
                username,
                password
            )
        )
        return conn

    def _get_files_list(self, folder_name):
        conn = self._auth()
        target_folder_url = f'/sites/{sharepoint_site_name}/{sharepoint_doc}/{folder_name}'
        root_folder = conn.web.get_folder_by_server_relative_url(target_folder_url)
        root_folder.expand(['Files', 'Folders']).get().execute_query()
        return root_folder.files

    def download_file(self, file_name, folder_name):
        try:
            conn = self._auth()
            file_url = f'/sites/{sharepoint_site_name}/{sharepoint_doc}/{folder_name}/{file_name}'
            file = File.open_binary(conn, file_url)
            return file.content
        except Exception as e:
            raise Exception(f"Erro ao baixar arquivo {file_name}: {str(e)}")

    def upload_file(self, file_name, folder_name, content):
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