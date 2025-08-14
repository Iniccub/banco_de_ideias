import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from mongodb_connection import mongo_manager
from collections import Counter

def calcular_pontos_usuario(ideias_usuario):
    """Calcula pontos baseado nas atividades do usuário"""
    pontos = 0
    
    for ideia in ideias_usuario:
        # Pontos por enviar ideia
        pontos += 10
        
        # Pontos extras por status
        status = ideia.get('status', 'Pendente')
        if status == 'Aprovada':
            pontos += 20
        elif status == 'Implementada':
            pontos += 50
        
        # Pontos por prioridade
        prioridade = ideia.get('prioridade', 'Média')
        if prioridade == 'Alta':
            pontos += 15
        elif prioridade == 'Crítica':
            pontos += 25
    
    return pontos

def verificar_badges(ideias_usuario):
    """Verifica quais badges o usuário conquistou"""
    badges = []
    total_ideias = len(ideias_usuario)
    ideias_implementadas = len([i for i in ideias_usuario if i.get('status') == 'Implementada'])
    
    # Badge: Primeira Ideia
    if total_ideias >= 1:
        badges.append('🚀 Primeira Ideia')
    
    # Badge: Inovador
    if total_ideias >= 5:
        badges.append('💡 Inovador')
    
    # Badge: Super Inovador
    if total_ideias >= 10:
        badges.append('🌟 Super Inovador')
    
    # Badge: Certeiro
    if ideias_implementadas >= 1:
        badges.append('🎯 Certeiro')
    
    # Badge: Master
    if ideias_implementadas >= 3:
        badges.append('🏆 Master')
    
    # Badge: Em Chamas (3 ideias na última semana)
    uma_semana_atras = datetime.now() - timedelta(days=7)
    ideias_semana = [i for i in ideias_usuario 
                    if isinstance(i.get('data_criacao'), datetime) and 
                    i.get('data_criacao') >= uma_semana_atras]
    
    if len(ideias_semana) >= 3:
        badges.append('🔥 Em Chamas')
    
    return badges

def obter_titulo_badge(pontos):
    """Retorna o título baseado nos pontos"""
    if pontos >= 1000:
        return '🥇 Inovador Master'
    elif pontos >= 750:
        return '🥈 Criativo Pro'
    elif pontos >= 500:
        return '🥉 Idealizador'
    elif pontos >= 250:
        return '🌟 Colaborador'
    elif pontos >= 100:
        return '💡 Iniciante'
    else:
        return '🌱 Novato'

def criar_sistema_gamificacao():
    st.header("🎮 Sistema de Gamificação")
    
    # Buscar dados do MongoDB
    ideias = mongo_manager.buscar_ideias()
    
    if not ideias:
        st.warning("⚠️ Nenhuma ideia encontrada no banco de dados.")
        st.info("💡 Cadastre algumas ideias primeiro para ver a gamificação.")
        return
    
    # Agrupar ideias por autor
    ideias_por_autor = {}
    for ideia in ideias:
        autor = ideia.get('autor', 'Anônimo')
        if autor and autor != 'Anônimo':
            if autor not in ideias_por_autor:
                ideias_por_autor[autor] = []
            ideias_por_autor[autor].append(ideia)
    
    if not ideias_por_autor:
        st.info("👥 Nenhum colaborador identificado (todas as ideias são anônimas).")
        return
    
    # Calcular ranking
    ranking_dados = []
    for autor, ideias_usuario in ideias_por_autor.items():
        pontos = calcular_pontos_usuario(ideias_usuario)
        badges = verificar_badges(ideias_usuario)
        titulo = obter_titulo_badge(pontos)
        
        ideias_implementadas = len([i for i in ideias_usuario if i.get('status') == 'Implementada'])
        
        ranking_dados.append({
            'Colaborador': autor,
            'Pontos': pontos,
            'Ideias Enviadas': len(ideias_usuario),
            'Ideias Implementadas': ideias_implementadas,
            'Badge': titulo,
            'Badges Conquistados': len(badges)
        })
    
    # Ordenar por pontos
    ranking_dados.sort(key=lambda x: x['Pontos'], reverse=True)
    
    # Adicionar posição
    for i, dados in enumerate(ranking_dados):
        dados['Posição'] = i + 1
    
    # Ranking de colaboradores
    st.subheader("🏆 Ranking de Inovadores")
    
    # Criar DataFrame para exibição
    df_ranking = pd.DataFrame(ranking_dados)
    
    # Reordenar colunas
    colunas_ordem = ['Posição', 'Colaborador', 'Pontos', 'Ideias Enviadas', 'Ideias Implementadas', 'Badge', 'Badges Conquistados']
    df_ranking = df_ranking[colunas_ordem]
    
    # Destacar top 3
    def destacar_top3(row):
        if row['Posição'] == 1:
            return ['background-color: #FFD700'] * len(row)  # Ouro
        elif row['Posição'] == 2:
            return ['background-color: #C0C0C0'] * len(row)  # Prata
        elif row['Posição'] == 3:
            return ['background-color: #CD7F32'] * len(row)  # Bronze
        else:
            return [''] * len(row)
    
    st.dataframe(df_ranking.style.apply(destacar_top3, axis=1), use_container_width=True)
    
    # Gráfico de pontuação
    if len(df_ranking) > 1:
        st.subheader("📊 Distribuição de Pontos")
        
        fig_pontos = px.bar(df_ranking.head(10), 
                           x='Colaborador', y='Pontos',
                           title='Top 10 Colaboradores por Pontuação',
                           color='Pontos',
                           color_continuous_scale='viridis')
        fig_pontos.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_pontos, use_container_width=True)
    
    # Sistema de badges
    st.subheader("🏅 Sistema de Badges")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        **🚀 Primeira Ideia**
        Enviou sua primeira ideia
        
        *Conquistado por:* {}
        """.format(len([u for u in ideias_por_autor if len(ideias_por_autor[u]) >= 1])))
    
    with col2:
        st.markdown("""
        **💡 Inovador**
        5 ideias enviadas
        
        *Conquistado por:* {}
        """.format(len([u for u in ideias_por_autor if len(ideias_por_autor[u]) >= 5])))
    
    with col3:
        st.markdown("""
        **🎯 Certeiro**
        Ideia implementada
        
        *Conquistado por:* {}
        """.format(len([u for u in ideias_por_autor 
                       if len([i for i in ideias_por_autor[u] if i.get('status') == 'Implementada']) >= 1])))
    
    with col4:
        uma_semana_atras = datetime.now() - timedelta(days=7)
        usuarios_em_chamas = 0
        for usuario, ideias_usuario in ideias_por_autor.items():
            ideias_semana = [i for i in ideias_usuario 
                           if isinstance(i.get('data_criacao'), datetime) and 
                           i.get('data_criacao') >= uma_semana_atras]
            if len(ideias_semana) >= 3:
                usuarios_em_chamas += 1
        
        st.markdown("""
        **🔥 Em Chamas**
        3 ideias em uma semana
        
        *Conquistado por:* {}
        """.format(usuarios_em_chamas))
    
    # Badges adicionais
    st.subheader("🌟 Badges Especiais")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        super_inovadores = len([u for u in ideias_por_autor if len(ideias_por_autor[u]) >= 10])
        st.markdown("""
        **🌟 Super Inovador**
        10+ ideias enviadas
        
        *Conquistado por:* {}
        """.format(super_inovadores))
    
    with col2:
        masters = len([u for u in ideias_por_autor 
                      if len([i for i in ideias_por_autor[u] if i.get('status') == 'Implementada']) >= 3])
        st.markdown("""
        **🏆 Master**
        3+ ideias implementadas
        
        *Conquistado por:* {}
        """.format(masters))
    
    with col3:
        # Usuário mais ativo do mês
        inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        ideias_mes_por_usuario = {}
        
        for usuario, ideias_usuario in ideias_por_autor.items():
            ideias_mes = [i for i in ideias_usuario 
                         if isinstance(i.get('data_criacao'), datetime) and 
                         i.get('data_criacao') >= inicio_mes]
            ideias_mes_por_usuario[usuario] = len(ideias_mes)
        
        if ideias_mes_por_usuario:
            usuario_destaque = max(ideias_mes_por_usuario, key=ideias_mes_por_usuario.get)
            ideias_destaque = ideias_mes_por_usuario[usuario_destaque]
            
            st.markdown("""
            **⭐ Destaque do Mês**
            Mais ativo em {}
            
            *{}* - {} ideias
            """.format(datetime.now().strftime('%B'), usuario_destaque, ideias_destaque))
    
    # Desafios mensais
    st.subheader("🎯 Desafios Mensais")
    
    # Calcular estatísticas do mês atual
    inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    ideias_mes = [i for i in ideias if isinstance(i.get('data_criacao'), datetime) and i.get('data_criacao') >= inicio_mes]
    
    participantes_mes = set()
    for ideia in ideias_mes:
        autor = ideia.get('autor', 'Anônimo')
        if autor and autor != 'Anônimo':
            participantes_mes.add(autor)
    
    # Desafio baseado na categoria mais popular
    categorias_count = Counter([i.get('categoria', 'Geral') for i in ideias])
    categoria_popular = categorias_count.most_common(1)[0][0] if categorias_count else 'Sustentabilidade'
    
    mes_atual = datetime.now().strftime('%B')
    ano_atual = datetime.now().year
    
    st.info(f"""
    **Desafio de {mes_atual}: {categoria_popular}**
    
    Envie ideias relacionadas à categoria {categoria_popular}.
    
    🏆 Prêmio: Vale-presente de R$ 200
    
    ⏰ Prazo: {datetime.now().replace(month=datetime.now().month+1 if datetime.now().month < 12 else 1, day=1) - timedelta(days=1):%d/%m/%Y}
    
    📊 Participantes: {len(participantes_mes)} | Ideias: {len(ideias_mes)}
    """)
    
    # Progresso pessoal
    st.subheader("📈 Seu Progresso")
    
    # Seletor de usuário
    usuarios_disponiveis = list(ideias_por_autor.keys())
    if usuarios_disponiveis:
        usuario_selecionado = st.selectbox("Selecione um colaborador:", usuarios_disponiveis)
        
        if usuario_selecionado:
            ideias_usuario = ideias_por_autor[usuario_selecionado]
            pontos_usuario = calcular_pontos_usuario(ideias_usuario)
            badges_usuario = verificar_badges(ideias_usuario)
            titulo_usuario = obter_titulo_badge(pontos_usuario)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Pontos Totais", pontos_usuario)
            
            with col2:
                st.metric("Ideias Enviadas", len(ideias_usuario))
            
            with col3:
                implementadas = len([i for i in ideias_usuario if i.get('status') == 'Implementada'])
                st.metric("Ideias Implementadas", implementadas)
            
            st.write(f"**Título Atual:** {titulo_usuario}")
            
            if badges_usuario:
                st.write("**Badges Conquistados:**")
                for badge in badges_usuario:
                    st.write(f"• {badge}")
            else:
                st.write("**Nenhum badge conquistado ainda.**")
            
            # Próximo objetivo
            proximo_pontos = 0
            proximo_titulo = ""
            
            if pontos_usuario < 100:
                proximo_pontos = 100
                proximo_titulo = "💡 Iniciante"
            elif pontos_usuario < 250:
                proximo_pontos = 250
                proximo_titulo = "🌟 Colaborador"
            elif pontos_usuario < 500:
                proximo_pontos = 500
                proximo_titulo = "🥉 Idealizador"
            elif pontos_usuario < 750:
                proximo_pontos = 750
                proximo_titulo = "🥈 Criativo Pro"
            elif pontos_usuario < 1000:
                proximo_pontos = 1000
                proximo_titulo = "🥇 Inovador Master"
            
            if proximo_pontos > 0:
                pontos_faltantes = proximo_pontos - pontos_usuario
                st.progress(pontos_usuario / proximo_pontos)
                st.write(f"**Próximo objetivo:** {proximo_titulo} (faltam {pontos_faltantes} pontos)")
    
    # Botão para atualizar dados
    if st.button("🔄 Atualizar Ranking"):
        st.rerun()