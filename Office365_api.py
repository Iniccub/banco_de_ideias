
import os
import streamlit as st
from dotenv import load_dotenv
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.files.file import File

# Carrega variáveis do arquivo .env
load_dotenv()

# Tenta obter as credenciais do st.secrets (Streamlit Cloud) ou do .env (ambiente local)
try:
    # Tenta usar st.secrets (Streamlit Cloud)
    username = st.secrets["sharepoint"]["sharepoint_email"]
    password = st.secrets["sharepoint"]["sharepoint_password"]
    sharepoint_site = st.secrets["sharepoint"]["sharepoint_url_site"]
    sharepoint_site_name = st.secrets["sharepoint"]["sharepoint_site_name"]
    sharepoint_doc = st.secrets["sharepoint"]["sharepoint_doc_library"]
except (KeyError, AttributeError):
    # Fallback para variáveis de ambiente locais (.env)
    username = os.getenv("sharepoint_email")
    password = os.getenv("sharepoint_password")
    sharepoint_site = os.getenv("sharepoint_url_site")
    sharepoint_site_name = os.getenv("sharepoint_site_name")
    sharepoint_doc = os.getenv("sharepoint_doc_library")


class SharePoint:
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
        conn = self._auth()
        # Corrigir o caminho para incluir o nome do arquivo
        file_url = f'/sites/{sharepoint_site_name}/{sharepoint_doc}/{folder_name}/{file_name}'
        file = File.open_binary(conn, file_url)
        return file.content

    def upload_file(self, file_name, folder_name, content):
        conn = self._auth()
        target_folder_url = f'/sites/{sharepoint_site_name}/{sharepoint_doc}/{folder_name}'
        target_folder = conn.web.get_folder_by_server_relative_path(target_folder_url)
        response = target_folder.upload_file(file_name, content).execute_query()
        return response

# Exportar a classe SharePoint
__all__ = ['SharePoint']
                