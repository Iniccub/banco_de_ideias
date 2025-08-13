import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from textblob import TextBlob
import nltk
from collections import Counter
import re
# Adicionar as importações faltando
import pandas as pd
import plotly.express as px

def criar_analise_texto():
    st.header("☁️ Análise de Texto das Ideias")
    
    # Nuvem de palavras
    st.subheader("Nuvem de Palavras Mais Frequentes")
    
    # Simulação de dados de texto das ideias
    textos_ideias = [
        "inovação tecnológica educação digital",
        "sustentabilidade meio ambiente verde",
        "metodologia ativa aprendizagem colaborativa"
    ]
    
    texto_completo = " ".join(textos_ideias)
    
    if texto_completo:
        try:
            wordcloud = WordCloud(width=800, height=400, 
                                 background_color='white',
                                 colormap='viridis').generate(texto_completo)
            
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Erro ao gerar nuvem de palavras: {e}")
            st.info("Instale as dependências: pip install wordcloud matplotlib")
    
    # Análise de sentimentos
    st.subheader("😊 Análise de Sentimentos")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Positivas", "78%", "+5%")
    with col2:
        st.metric("Neutras", "18%", "-2%")
    with col3:
        st.metric("Negativas", "4%", "-3%")
    
    # Palavras-chave mais frequentes
    st.subheader("🔤 Palavras-chave Mais Frequentes")
    
    palavras_freq = Counter({
        'inovação': 45, 'educação': 38, 'tecnologia': 32,
        'sustentabilidade': 28, 'metodologia': 25, 'colaboração': 22
    })
    
    try:
        df_palavras = pd.DataFrame(list(palavras_freq.items()), 
                                  columns=['Palavra', 'Frequência'])
        
        fig_palavras = px.bar(df_palavras.head(10), x='Palavra', y='Frequência',
                             title='Top 10 Palavras Mais Frequentes')
        st.plotly_chart(fig_palavras, use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao gerar gráfico: {e}")
        # Fallback: mostrar dados em tabela simples
        st.write("**Palavras mais frequentes:**")
        for palavra, freq in palavras_freq.most_common(10):
            st.write(f"- {palavra}: {freq}")