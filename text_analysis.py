import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from textblob import TextBlob
import nltk
from collections import Counter
import re
import pandas as pd
import plotly.express as px
from mongodb_connection import mongo_manager
import numpy as np
from datetime import datetime

# Baixar recursos do NLTK se necessário
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    try:
        nltk.download('punkt', quiet=True)
    except:
        pass

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    try:
        nltk.download('stopwords', quiet=True)
    except:
        pass

def limpar_texto(texto):
    """Limpa e processa o texto para análise"""
    if not texto:
        return ""
    
    # Converter para minúsculas
    texto = texto.lower()
    
    # Remover caracteres especiais e números
    texto = re.sub(r'[^a-záàâãéèêíïóôõöúçñ\s]', '', texto)
    
    # Remover palavras muito curtas
    palavras = texto.split()
    palavras = [palavra for palavra in palavras if len(palavra) > 2]
    
    # Remover stopwords em português
    stopwords_pt = {
        'de', 'da', 'do', 'das', 'dos', 'para', 'com', 'em', 'na', 'no', 'nas', 'nos',
        'e', 'ou', 'a', 'o', 'as', 'os', 'um', 'uma', 'uns', 'umas', 'que', 'se', 'por',
        'mais', 'muito', 'ser', 'ter', 'fazer', 'como', 'sobre', 'quando', 'onde',
        'porque', 'mas', 'também', 'já', 'ainda', 'só', 'bem', 'pode', 'vai', 'tem',
        'são', 'foi', 'será', 'está', 'estava', 'estão', 'foram', 'sendo', 'sido'
    }
    
    palavras_filtradas = [palavra for palavra in palavras if palavra not in stopwords_pt]
    
    return ' '.join(palavras_filtradas)

def analisar_sentimento(texto):
    """Analisa o sentimento do texto usando TextBlob"""
    try:
        blob = TextBlob(texto)
        polaridade = blob.sentiment.polarity
        
        if polaridade > 0.1:
            return 'positivo'
        elif polaridade < -0.1:
            return 'negativo'
        else:
            return 'neutro'
    except:
        return 'neutro'

def criar_analise_texto():
    st.header("☁️ Análise de Texto das Ideias")
    
    # Buscar dados do MongoDB
    ideias = mongo_manager.buscar_ideias()
    
    if not ideias:
        st.warning("⚠️ Nenhuma ideia encontrada no banco de dados.")
        st.info("💡 Cadastre algumas ideias primeiro para ver as análises de texto.")
        return
    
    # Coletar textos das ideias
    textos_titulos = []
    textos_descricoes = []
    textos_completos = []
    
    for ideia in ideias:
        titulo = ideia.get('titulo', '')
        descricao = ideia.get('descricao', '')
        
        if titulo:
            textos_titulos.append(titulo)
            textos_completos.append(titulo)
        
        if descricao:
            textos_descricoes.append(descricao)
            textos_completos.append(descricao)
    
    if not textos_completos:
        st.info("📝 Nenhum texto disponível para análise.")
        return
    
    # Nuvem de palavras
    st.subheader("☁️ Nuvem de Palavras Mais Frequentes")
    
    # Processar texto para nuvem de palavras
    texto_para_nuvem = ' '.join([limpar_texto(texto) for texto in textos_completos])
    
    if texto_para_nuvem.strip():
        try:
            wordcloud = WordCloud(
                width=800, 
                height=400,
                background_color='white',
                colormap='viridis',
                max_words=100,
                relative_scaling=0.5,
                min_font_size=10
            ).generate(texto_para_nuvem)
            
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
            
        except Exception as e:
            st.error(f"Erro ao gerar nuvem de palavras: {e}")
            st.info("💡 Certifique-se de que as bibliotecas wordcloud e matplotlib estão instaladas.")
    else:
        st.info("📝 Texto insuficiente para gerar nuvem de palavras.")
    
    # Análise de sentimentos
    st.subheader("😊 Análise de Sentimentos")
    
    # Analisar sentimentos de títulos e descrições
    sentimentos = []
    for texto in textos_completos:
        if texto.strip():
            sentimento = analisar_sentimento(texto)
            sentimentos.append(sentimento)
    
    if sentimentos:
        contador_sentimentos = Counter(sentimentos)
        total_textos = len(sentimentos)
        
        positivos = contador_sentimentos.get('positivo', 0)
        neutros = contador_sentimentos.get('neutro', 0)
        negativos = contador_sentimentos.get('negativo', 0)
        
        perc_positivos = (positivos / total_textos * 100) if total_textos > 0 else 0
        perc_neutros = (neutros / total_textos * 100) if total_textos > 0 else 0
        perc_negativos = (negativos / total_textos * 100) if total_textos > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Positivas", f"{perc_positivos:.1f}%", f"{positivos} textos")
        with col2:
            st.metric("Neutras", f"{perc_neutros:.1f}%", f"{neutros} textos")
        with col3:
            st.metric("Negativas", f"{perc_negativos:.1f}%", f"{negativos} textos")
        
        # Gráfico de pizza dos sentimentos
        if any([positivos, neutros, negativos]):
            df_sentimentos = pd.DataFrame({
                'Sentimento': ['Positivo', 'Neutro', 'Negativo'],
                'Quantidade': [positivos, neutros, negativos],
                'Porcentagem': [perc_positivos, perc_neutros, perc_negativos]
            })
            
            # Filtrar apenas sentimentos com valores > 0
            df_sentimentos = df_sentimentos[df_sentimentos['Quantidade'] > 0]
            
            if not df_sentimentos.empty:
                cores_sentimentos = {
                    'Positivo': '#2E8B57',
                    'Neutro': '#FFD700', 
                    'Negativo': '#DC143C'
                }
                
                fig_sentimentos = px.pie(
                    df_sentimentos, 
                    values='Quantidade', 
                    names='Sentimento',
                    title='Distribuição de Sentimentos',
                    color='Sentimento',
                    color_discrete_map=cores_sentimentos
                )
                st.plotly_chart(fig_sentimentos, use_container_width=True)
    else:
        st.info("📊 Não foi possível analisar sentimentos dos textos.")
    
    # Palavras-chave mais frequentes
    st.subheader("🔤 Palavras-chave Mais Frequentes")
    
    # Processar todos os textos para extrair palavras-chave
    todas_palavras = []
    for texto in textos_completos:
        texto_limpo = limpar_texto(texto)
        if texto_limpo:
            todas_palavras.extend(texto_limpo.split())
    
    if todas_palavras:
        contador_palavras = Counter(todas_palavras)
        palavras_mais_comuns = contador_palavras.most_common(20)
        
        if palavras_mais_comuns:
            df_palavras = pd.DataFrame(palavras_mais_comuns, columns=['Palavra', 'Frequência'])
            
            # Gráfico de barras das palavras mais frequentes
            fig_palavras = px.bar(
                df_palavras.head(15), 
                x='Frequência', 
                y='Palavra',
                title='Top 15 Palavras Mais Frequentes',
                orientation='h',
                color='Frequência',
                color_continuous_scale='viridis'
            )
            fig_palavras.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_palavras, use_container_width=True)
            
            # Tabela das palavras mais frequentes
            st.subheader("📋 Tabela de Frequência")
            st.dataframe(df_palavras, use_container_width=True)
        else:
            st.info("📝 Nenhuma palavra-chave encontrada.")
    else:
        st.info("📝 Texto insuficiente para análise de palavras-chave.")
    
    # Análise por categoria
    st.subheader("📊 Análise por Categoria")
    
    # Agrupar textos por categoria
    textos_por_categoria = {}
    for ideia in ideias:
        categoria = ideia.get('categoria', 'Não categorizada')
        titulo = ideia.get('titulo', '')
        descricao = ideia.get('descricao', '')
        
        if categoria not in textos_por_categoria:
            textos_por_categoria[categoria] = []
        
        if titulo:
            textos_por_categoria[categoria].append(titulo)
        if descricao:
            textos_por_categoria[categoria].append(descricao)
    
    if textos_por_categoria:
        # Calcular estatísticas por categoria
        stats_categoria = []
        
        for categoria, textos in textos_por_categoria.items():
            if textos:
                # Contar palavras totais
                total_palavras = sum(len(limpar_texto(texto).split()) for texto in textos)
                
                # Analisar sentimentos
                sentimentos_cat = [analisar_sentimento(texto) for texto in textos if texto.strip()]
                positivos_cat = sentimentos_cat.count('positivo')
                
                # Palavras mais comuns da categoria
                palavras_cat = []
                for texto in textos:
                    palavras_cat.extend(limpar_texto(texto).split())
                
                palavra_mais_comum = ''
                if palavras_cat:
                    palavra_mais_comum = Counter(palavras_cat).most_common(1)[0][0]
                
                stats_categoria.append({
                    'Categoria': categoria,
                    'Textos': len(textos),
                    'Total Palavras': total_palavras,
                    'Sentimentos Positivos': positivos_cat,
                    'Palavra Mais Comum': palavra_mais_comum
                })
        
        if stats_categoria:
            df_stats = pd.DataFrame(stats_categoria)
            st.dataframe(df_stats, use_container_width=True)
    
    # Análise temporal
    st.subheader("📅 Análise Temporal")
    
    # Agrupar por mês
    textos_por_mes = {}
    for ideia in ideias:
        data_criacao = ideia.get('data_criacao')
        if isinstance(data_criacao, datetime):
            mes_ano = data_criacao.strftime('%Y-%m')
            
            if mes_ano not in textos_por_mes:
                textos_por_mes[mes_ano] = []
            
            titulo = ideia.get('titulo', '')
            descricao = ideia.get('descricao', '')
            
            if titulo:
                textos_por_mes[mes_ano].append(titulo)
            if descricao:
                textos_por_mes[mes_ano].append(descricao)
    
    if textos_por_mes:
        # Calcular volume de texto por mês
        dados_temporais = []
        for mes, textos in sorted(textos_por_mes.items()):
            total_palavras = sum(len(limpar_texto(texto).split()) for texto in textos)
            
            dados_temporais.append({
                'Mês': datetime.strptime(mes, '%Y-%m').strftime('%b/%Y'),
                'Total Palavras': total_palavras,
                'Número de Textos': len(textos)
            })
        
        if dados_temporais:
            df_temporal = pd.DataFrame(dados_temporais)
            
            fig_temporal = px.line(
                df_temporal, 
                x='Mês', 
                y='Total Palavras',
                title='Volume de Texto por Mês',
                markers=True
            )
            fig_temporal.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_temporal, use_container_width=True)
    
    # Estatísticas gerais
    st.subheader("📈 Estatísticas Gerais")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Textos", len(textos_completos))
    
    with col2:
        total_palavras_geral = len(todas_palavras) if todas_palavras else 0
        st.metric("Total de Palavras", total_palavras_geral)
    
    with col3:
        palavras_unicas = len(set(todas_palavras)) if todas_palavras else 0
        st.metric("Palavras Únicas", palavras_unicas)
    
    with col4:
        media_palavras = (total_palavras_geral / len(textos_completos)) if textos_completos else 0
        st.metric("Média Palavras/Texto", f"{media_palavras:.1f}")
    
    # Botão para atualizar análise
    if st.button("🔄 Atualizar Análise"):
        st.rerun()