import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import re
from datetime import datetime, timedelta

def criar_dashboard_analytics():
    st.header("📊 Dashboard de Analytics - Banco de Ideias")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Ideias", "127", "+12")
    with col2:
        st.metric("Ideias este Mês", "23", "+5")
    with col3:
        st.metric("Colaboradores Ativos", "45", "+3")
    with col4:
        st.metric("Taxa de Implementação", "18%", "+2%")
    
    # Gráficos de tendências
    st.subheader("📈 Tendências Temporais")
    
    # Gráfico de ideias por mês
    dados_tempo = pd.DataFrame({
        'Mês': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
        'Ideias': [15, 22, 18, 25, 20, 23]
    })
    
    fig_tempo = px.line(dados_tempo, x='Mês', y='Ideias', 
                       title='Evolução de Ideias por Mês')
    st.plotly_chart(fig_tempo, use_container_width=True)
    
    # Distribuição por categoria
    st.subheader("🎯 Distribuição por Categoria")
    
    dados_categoria = pd.DataFrame({
        'Categoria': ['Tecnologia & Inovação', 'Currículo & Metodologia', 
                     'Infraestrutura', 'Bem Estar', 'Eventos'],
        'Quantidade': [35, 28, 22, 18, 24]
    })
    
    fig_categoria = px.pie(dados_categoria, values='Quantidade', names='Categoria',
                          title='Ideias por Categoria')
    st.plotly_chart(fig_categoria, use_container_width=True)