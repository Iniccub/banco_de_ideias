import streamlit as st
from datetime import datetime, timedelta

def criar_sistema_notificacoes():
    st.header("🔔 Central de Notificações")
    
    # Notificações recentes
    st.subheader("📬 Notificações Recentes")
    
    notificacoes = [
        {
            'tipo': '✅',
            'titulo': 'Ideia Aprovada!',
            'mensagem': 'Sua ideia "App Mobile Educativo" foi aprovada para implementação.',
            'tempo': '2 horas atrás'
        },
        {
            'tipo': '💬',
            'titulo': 'Novo Comentário',
            'mensagem': 'A equipe de TI comentou em sua ideia sobre sistema de feedback.',
            'tempo': '1 dia atrás'
        },
        {
            'tipo': '🏆',
            'titulo': 'Nova Badge Conquistada!',
            'mensagem': 'Você conquistou a badge "Inovador" por enviar 5 ideias.',
            'tempo': '3 dias atrás'
        }
    ]
    
    for notif in notificacoes:
        with st.container():
            col1, col2 = st.columns([1, 10])
            with col1:
                st.write(notif['tipo'])
            with col2:
                st.write(f"**{notif['titulo']}**")
                st.write(notif['mensagem'])
                st.caption(notif['tempo'])
            st.divider()
    
    # Configurações de notificação
    st.subheader("⚙️ Configurações de Notificação")
    
    st.checkbox("📧 Receber por email", value=True)
    st.checkbox("📱 Notificações push", value=True)
    st.checkbox("🔔 Notificações de aprovação", value=True)
    st.checkbox("💬 Notificações de comentários", value=False)
    st.checkbox("🏆 Notificações de badges", value=True)