import streamlit as st

def criar_navegacao():
    # Menu lateral com páginas
    with st.sidebar:
        st.image("1_LOGO BIP.png", width=230)
        
        pagina = st.selectbox(
            "Navegação",
            [
                "🏠 Enviar Ideia",
                "📋 Listar Ideias",    # Nova opção
                "📊 Dashboard",
                "☁️ Análise de Texto",
                "📋 Controle de Ideias",
                "🎮 Gamificação",
                "🔔 Notificações",
                "🤖 Análise IA"
            ]
        )
    
    return pagina