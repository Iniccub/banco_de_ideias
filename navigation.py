import streamlit as st
from auth import auth_manager

def criar_navegacao():
    # Menu lateral com páginas
    with st.sidebar:
        st.image("ICON BIP.PNG", width=230)
        
        # Seção de autenticação
        st.markdown("---")
        if auth_manager.is_authenticated():
            st.success(f"👤 Logado como: **{auth_manager.get_username()}**")
            if st.button("🚪 Logout", use_container_width=True):
                auth_manager.fazer_logout()
        else:
            st.info("👤 **Visitante** (acesso limitado)")
            st.caption("Faça login para acessar todas as funcionalidades")
        
        st.markdown("---")
        
        # Lista de páginas com indicadores de acesso
        paginas_opcoes = [
            "🏠 Enviar Ideia",
            "📋 Listar Ideias 🔒",
            "📊 Dashboard 🔒",
            "☁️ Análise de Texto 🔒",
            "📋 Controle de Ideias 🔒",
            "🎮 Gamificação 🔒",
            "🔔 Notificações 🔒",
            "🤖 Análise IA 🔒"
        ]
        
        pagina = st.selectbox(
            "Navegação",
            paginas_opcoes,
            help="🔒 = Requer login administrativo"
        )
        
        # Remove o ícone de cadeado para processamento interno
        pagina_limpa = pagina.replace(" 🔒", "")
    
    return pagina_limpa