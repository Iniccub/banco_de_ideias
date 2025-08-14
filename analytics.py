import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import re
from datetime import datetime, timedelta
from mongodb_connection import mongo_manager
import numpy as np

def criar_dashboard_analytics():
    st.header("📊 Dashboard de Analytics - Banco de Ideias")
    
    # Buscar dados do MongoDB
    ideias = mongo_manager.buscar_ideias()
    
    if not ideias:
        st.warning("⚠️ Nenhuma ideia encontrada no banco de dados.")
        st.info("💡 Cadastre algumas ideias primeiro para ver as análises.")
        return
    
    # Calcular métricas principais
    total_ideias = len(ideias)
    
    # Ideias deste mês
    inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    ideias_mes = len([i for i in ideias if isinstance(i.get('data_criacao'), datetime) and i.get('data_criacao') >= inicio_mes])
    
    # Colaboradores únicos
    autores_unicos = set()
    for ideia in ideias:
        autor = ideia.get('autor', 'Anônimo')
        if autor and autor != 'Anônimo':
            autores_unicos.add(autor)
    colaboradores_ativos = len(autores_unicos)
    
    # Taxa de implementação
    ideias_implementadas = len([i for i in ideias if i.get('status') == 'Implementada'])
    taxa_implementacao = (ideias_implementadas / total_ideias * 100) if total_ideias > 0 else 0
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Ideias", total_ideias)
    with col2:
        st.metric("Ideias este Mês", ideias_mes)
    with col3:
        st.metric("Colaboradores Ativos", colaboradores_ativos)
    with col4:
        st.metric("Taxa de Implementação", f"{taxa_implementacao:.1f}%")
    
    # Gráficos de tendências
    st.subheader("📈 Tendências Temporais")
    
    # Preparar dados para gráfico temporal
    dados_temporais = {}
    for ideia in ideias:
        data_criacao = ideia.get('data_criacao')
        if isinstance(data_criacao, datetime):
            mes_ano = data_criacao.strftime('%Y-%m')
            dados_temporais[mes_ano] = dados_temporais.get(mes_ano, 0) + 1
    
    if dados_temporais:
        # Ordenar por data
        meses_ordenados = sorted(dados_temporais.keys())
        
        # Criar DataFrame para o gráfico
        df_tempo = pd.DataFrame({
            'Mês': [datetime.strptime(mes, '%Y-%m').strftime('%b/%Y') for mes in meses_ordenados],
            'Ideias': [dados_temporais[mes] for mes in meses_ordenados]
        })
        
        fig_tempo = px.line(df_tempo, x='Mês', y='Ideias', 
                           title='Evolução de Ideias por Mês',
                           markers=True)
        fig_tempo.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_tempo, use_container_width=True)
    else:
        st.info("📅 Dados temporais insuficientes para gerar o gráfico.")
    
    # Distribuição por categoria
    st.subheader("🎯 Distribuição por Categoria")
    
    # Contar ideias por categoria
    categorias_count = {}
    for ideia in ideias:
        categoria = ideia.get('categoria', 'Não categorizada')
        categorias_count[categoria] = categorias_count.get(categoria, 0) + 1
    
    if categorias_count:
        df_categoria = pd.DataFrame({
            'Categoria': list(categorias_count.keys()),
            'Quantidade': list(categorias_count.values())
        })
        
        fig_categoria = px.pie(df_categoria, values='Quantidade', names='Categoria',
                              title='Ideias por Categoria')
        st.plotly_chart(fig_categoria, use_container_width=True)
    
    # Distribuição por status
    st.subheader("📊 Status das Ideias")
    
    # Contar ideias por status
    status_count = {}
    for ideia in ideias:
        status = ideia.get('status', 'Pendente')
        status_count[status] = status_count.get(status, 0) + 1
    
    if status_count:
        df_status = pd.DataFrame({
            'Status': list(status_count.keys()),
            'Quantidade': list(status_count.values())
        })
        
        # Definir cores para cada status
        cores_status = {
            'Pendente': '#FFA500',
            'Em Análise': '#1E90FF',
            'Aprovada': '#32CD32',
            'Implementada': '#228B22',
            'Rejeitada': '#DC143C'
        }
        
        cores = [cores_status.get(status, '#808080') for status in df_status['Status']]
        
        fig_status = px.bar(df_status, x='Status', y='Quantidade',
                           title='Distribuição por Status',
                           color='Status',
                           color_discrete_map=cores_status)
        st.plotly_chart(fig_status, use_container_width=True)
    
    # Top colaboradores
    st.subheader("🏆 Top Colaboradores")
    
    # Contar ideias por autor
    autores_count = {}
    for ideia in ideias:
        autor = ideia.get('autor', 'Anônimo')
        if autor and autor != 'Anônimo':
            autores_count[autor] = autores_count.get(autor, 0) + 1
    
    if autores_count:
        # Pegar top 10 colaboradores
        top_autores = sorted(autores_count.items(), key=lambda x: x[1], reverse=True)[:10]
        
        df_autores = pd.DataFrame({
            'Colaborador': [autor for autor, count in top_autores],
            'Ideias': [count for autor, count in top_autores]
        })
        
        fig_autores = px.bar(df_autores, x='Ideias', y='Colaborador',
                            title='Top 10 Colaboradores por Número de Ideias',
                            orientation='h')
        fig_autores.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_autores, use_container_width=True)
    else:
        st.info("👥 Nenhum colaborador identificado (todas as ideias são anônimas).")
    
    # Nuvem de palavras
    st.subheader("☁️ Nuvem de Palavras - Títulos das Ideias")
    
    # Coletar todos os títulos
    titulos = []
    for ideia in ideias:
        titulo = ideia.get('titulo', '')
        if titulo:
            titulos.append(titulo)
    
    if titulos:
        # Juntar todos os títulos
        texto_completo = ' '.join(titulos)
        
        # Remover palavras comuns e caracteres especiais
        texto_limpo = re.sub(r'[^\w\s]', '', texto_completo.lower())
        palavras_comuns = ['de', 'da', 'do', 'das', 'dos', 'para', 'com', 'em', 'na', 'no', 'nas', 'nos', 'e', 'ou', 'a', 'o', 'as', 'os']
        palavras = [palavra for palavra in texto_limpo.split() if palavra not in palavras_comuns and len(palavra) > 2]
        
        if palavras:
            # Gerar nuvem de palavras
            wordcloud = WordCloud(width=800, height=400, 
                                 background_color='white',
                                 colormap='viridis',
                                 max_words=100).generate(' '.join(palavras))
            
            # Exibir nuvem de palavras
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
        else:
            st.info("📝 Texto insuficiente para gerar nuvem de palavras.")
    else:
        st.info("📝 Nenhum título disponível para análise.")
    
    # Análise de prioridades
    st.subheader("⚡ Análise de Prioridades")
    
    # Contar ideias por prioridade
    prioridades_count = {}
    for ideia in ideias:
        prioridade = ideia.get('prioridade', 'Média')
        prioridades_count[prioridade] = prioridades_count.get(prioridade, 0) + 1
    
    if prioridades_count:
        df_prioridades = pd.DataFrame({
            'Prioridade': list(prioridades_count.keys()),
            'Quantidade': list(prioridades_count.values())
        })
        
        # Definir ordem e cores para prioridades
        ordem_prioridade = ['Crítica', 'Alta', 'Média', 'Baixa']
        cores_prioridade = {
            'Crítica': '#DC143C',
            'Alta': '#FF6347',
            'Média': '#FFA500',
            'Baixa': '#32CD32'
        }
        
        # Reordenar DataFrame
        df_prioridades['Ordem'] = df_prioridades['Prioridade'].map({p: i for i, p in enumerate(ordem_prioridade)})
        df_prioridades = df_prioridades.sort_values('Ordem')
        
        fig_prioridades = px.bar(df_prioridades, x='Prioridade', y='Quantidade',
                                title='Distribuição por Prioridade',
                                color='Prioridade',
                                color_discrete_map=cores_prioridade)
        st.plotly_chart(fig_prioridades, use_container_width=True)
    
    # Estatísticas detalhadas
    st.subheader("📋 Estatísticas Detalhadas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Por Status:**")
        for status, count in sorted(status_count.items()):
            porcentagem = (count / total_ideias * 100) if total_ideias > 0 else 0
            st.write(f"• {status}: {count} ({porcentagem:.1f}%)")
    
    with col2:
        st.write("**Por Categoria:**")
        for categoria, count in sorted(categorias_count.items(), key=lambda x: x[1], reverse=True):
            porcentagem = (count / total_ideias * 100) if total_ideias > 0 else 0
            st.write(f"• {categoria}: {count} ({porcentagem:.1f}%)")
    
    # Botão para atualizar dados
    if st.button("🔄 Atualizar Dashboard"):
        st.rerun()