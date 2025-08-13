import streamlit as st
import plotly.express as px
import pandas as pd

def criar_sistema_gamificacao():
    st.header("🎮 Sistema de Gamificação")
    
    # Ranking de colaboradores
    st.subheader("🏆 Ranking de Inovadores")
    
    ranking_data = pd.DataFrame({
        'Posição': [1, 2, 3, 4, 5],
        'Colaborador': ['Maria Silva', 'João Santos', 'Ana Costa', 'Pedro Lima', 'Carla Souza'],
        'Pontos': [850, 720, 680, 540, 480],
        'Ideias Enviadas': [12, 9, 8, 6, 5],
        'Ideias Implementadas': [4, 3, 3, 2, 2],
        'Badge': ['🥇 Inovador Master', '🥈 Criativo Pro', '🥉 Idealizador', '🌟 Colaborador', '💡 Iniciante']
    })
    
    st.dataframe(ranking_data, use_container_width=True)
    
    # Sistema de badges
    st.subheader("🏅 Sistema de Badges")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        **🚀 Primeira Ideia**
        Enviou sua primeira ideia
        """)
    
    with col2:
        st.markdown("""
        **💡 Inovador**
        5 ideias enviadas
        """)
    
    with col3:
        st.markdown("""
        **🎯 Certeiro**
        Ideia implementada
        """)
    
    with col4:
        st.markdown("""
        **🔥 Em Chamas**
        3 ideias em uma semana
        """)
    
    # Desafios mensais
    st.subheader("🎯 Desafios Mensais")
    
    st.info("""
    **Desafio de Janeiro: Sustentabilidade**
    
    Envie ideias relacionadas à sustentabilidade e meio ambiente.
    
    🏆 Prêmio: Vale-presente de R$ 200
    
    ⏰ Prazo: 31/01/2024
    
    📊 Participantes: 23 | Ideias: 45
    """)