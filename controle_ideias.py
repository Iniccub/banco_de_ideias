import streamlit as st
import pandas as pd
from datetime import datetime

def criar_sistema_controle():
    st.header("📋 Sistema de Controle de Ideias")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox("Status", 
            ["Todas", "Pendente", "Em Análise", "Aprovada", "Implementada", "Rejeitada"])
    
    with col2:
        categoria_filter = st.selectbox("Categoria", 
            ["Todas", "Tecnologia & Inovação", "Currículo & Metodologia", 
             "Infraestrutura", "Bem Estar"])
    
    with col3:
        periodo_filter = st.selectbox("Período", 
            ["Todos", "Última semana", "Último mês", "Últimos 3 meses"])
    
    # Tabela de ideias com controle
    st.subheader("📊 Lista de Ideias")
    
    # Dados simulados
    dados_ideias = pd.DataFrame({
        'ID': ['BIP-001', 'BIP-002', 'BIP-003', 'BIP-004'],
        'Título': ['App Mobile Educativo', 'Horta Sustentável', 
                  'Metodologia Gamificada', 'Sistema de Feedback'],
        'Autor': ['João Silva', 'Anônimo', 'Maria Santos', 'Pedro Costa'],
        'Categoria': ['Tecnologia', 'Sustentabilidade', 'Metodologia', 'Gestão'],
        'Status': ['Em Análise', 'Aprovada', 'Pendente', 'Implementada'],
        'Data': ['2024-01-15', '2024-01-10', '2024-01-20', '2024-01-05'],
        'Prioridade': ['Alta', 'Média', 'Alta', 'Baixa'],
        'Responsável': ['TI', 'Infraestrutura', 'Pedagógico', 'RH']
    })
    
    # Exibir tabela editável
    edited_df = st.data_editor(
        dados_ideias,
        column_config={
            "Status": st.column_config.SelectboxColumn(
                "Status",
                options=["Pendente", "Em Análise", "Aprovada", "Implementada", "Rejeitada"]
            ),
            "Prioridade": st.column_config.SelectboxColumn(
                "Prioridade",
                options=["Baixa", "Média", "Alta", "Crítica"]
            )
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Ações em lote
    st.subheader("⚡ Ações em Lote")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📧 Enviar Feedback"):
            st.success("Feedback enviado para os autores selecionados!")
    
    with col2:
        if st.button("📊 Gerar Relatório"):
            st.success("Relatório gerado com sucesso!")
    
    with col3:
        if st.button("🔄 Atualizar Status"):
            st.success("Status atualizados!")