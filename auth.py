import streamlit as st
import hashlib

class AuthManager:
    def __init__(self):
        # Credenciais do administrador (podem ser movidas para secrets.toml)
        self.admin_credentials = {
            "admin": self._hash_password("admin123"),  # Usuário: admin, Senha: admin123
            "felipe": self._hash_password("felipe2025")  # Usuário: felipe, Senha: felipe2025
        }
    
    def _hash_password(self, password):
        """Cria hash da senha para segurança"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verificar_credenciais(self, username, password):
        """Verifica se as credenciais são válidas"""
        if username in self.admin_credentials:
            return self.admin_credentials[username] == self._hash_password(password)
        return False
    
    def fazer_login(self):
        """Interface de login"""
        st.subheader("🔐 Login Administrativo")
        
        with st.form("login_form"):
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            submit_button = st.form_submit_button("Entrar")
            
            if submit_button:
                if self.verificar_credenciais(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.success(f"✅ Login realizado com sucesso! Bem-vindo, {username}!")
                    st.rerun()
                else:
                    st.error("❌ Credenciais inválidas. Tente novamente.")
    
    def fazer_logout(self):
        """Realiza logout do usuário"""
        st.session_state.authenticated = False
        st.session_state.username = None
        st.success("✅ Logout realizado com sucesso!")
        st.rerun()
    
    def is_authenticated(self):
        """Verifica se o usuário está autenticado"""
        return st.session_state.get('authenticated', False)
    
    def get_username(self):
        """Retorna o nome do usuário logado"""
        return st.session_state.get('username', None)
    
    def require_auth(self, page_name):
        """Verifica se a página requer autenticação"""
        # Páginas que NÃO requerem autenticação
        public_pages = ["🏠 Enviar Ideia"]
        
        if page_name not in public_pages:
            if not self.is_authenticated():
                st.warning(f"⚠️ Acesso restrito! A página '{page_name}' requer login administrativo.")
                st.info("💡 A página 'Enviar Ideia' está disponível para todos os usuários.")
                self.fazer_login()
                return False
        return True

# Instância global do gerenciador de autenticação
auth_manager = AuthManager()