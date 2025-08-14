import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from mongodb_connection import mongo_manager
from bson import ObjectId

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
             "Infraestrutura", "Bem Estar", "Sustentabilidade", "Gestão"])
    
    with col3:
        periodo_filter = st.selectbox("Período", 
            ["Todos", "Última semana", "Último mês", "Últimos 3 meses"])
    
    # Buscar dados do MongoDB
    filtros_mongo = {}
    
    # Aplicar filtros
    if status_filter != "Todas":
        filtros_mongo["status"] = status_filter
    
    if categoria_filter != "Todas":
        filtros_mongo["categoria"] = categoria_filter
    
    # Filtro de período
    if periodo_filter != "Todos":
        data_limite = datetime.now()
        if periodo_filter == "Última semana":
            data_limite -= timedelta(days=7)
        elif periodo_filter == "Último mês":
            data_limite -= timedelta(days=30)
        elif periodo_filter == "Últimos 3 meses":
            data_limite -= timedelta(days=90)
        
        filtros_mongo["data_criacao"] = {"$gte": data_limite}
    
    # Buscar ideias do MongoDB
    ideias = mongo_manager.buscar_ideias(filtros_mongo)
    
    # Tabela de ideias com controle
    st.subheader("📊 Lista de Ideias")
    
    if not ideias:
        st.info("🔍 Nenhuma ideia encontrada com os filtros aplicados.")
        return
    
    # Converter dados do MongoDB para DataFrame
    dados_para_tabela = []
    for ideia in ideias:
        dados_para_tabela.append({
            'ID': str(ideia['_id'])[:8],  # Primeiros 8 caracteres do ObjectId
            'Título': ideia.get('titulo', 'Sem título'),
            'Autor': ideia.get('autor', 'Anônimo'),
            'Categoria': ideia.get('categoria', 'Não categorizada'),
            'Status': ideia.get('status', 'Pendente'),
            'Data': ideia.get('data_criacao', datetime.now()).strftime('%Y-%m-%d') if isinstance(ideia.get('data_criacao'), datetime) else str(ideia.get('data_criacao', ''))[:10],
            'Prioridade': ideia.get('prioridade', 'Média'),
            'Responsável': ideia.get('responsavel', 'Não atribuído'),
            '_id_completo': str(ideia['_id'])  # Para referência interna
        })
    
    dados_ideias = pd.DataFrame(dados_para_tabela)
    
    # Exibir tabela editável
    edited_df = st.data_editor(
        dados_ideias.drop('_id_completo', axis=1),  # Não mostrar o ID completo
        column_config={
            "Status": st.column_config.SelectboxColumn(
                "Status",
                options=["Pendente", "Em Análise", "Aprovada", "Implementada", "Rejeitada"]
            ),
            "Prioridade": st.column_config.SelectboxColumn(
                "Prioridade",
                options=["Baixa", "Média", "Alta", "Crítica"]
            ),
            "Responsável": st.column_config.SelectboxColumn(
                "Responsável",
                options=["Não atribuído", "TI", "Infraestrutura", "Pedagógico", "RH", "Direção"]
            )
        },
        hide_index=True,
        use_container_width=True,
        key="tabela_ideias"
    )
    
    # Detectar mudanças e atualizar no MongoDB
    if st.button("💾 Salvar Alterações", type="primary"):
        alteracoes_salvas = 0
        
        for index, row in edited_df.iterrows():
            if index < len(dados_ideias):
                id_original = dados_ideias.iloc[index]['_id_completo']
                
                # Verificar se houve mudanças
                dados_originais = dados_ideias.iloc[index]
                mudancas = {}
                
                if row['Status'] != dados_originais['Status']:
                    mudancas['status'] = row['Status']
                
                if row['Prioridade'] != dados_originais['Prioridade']:
                    mudancas['prioridade'] = row['Prioridade']
                
                if row['Responsável'] != dados_originais['Responsável']:
                    mudancas['responsavel'] = row['Responsável']
                
                # Se houver mudanças, atualizar no MongoDB
                if mudancas:
                    if mongo_manager.atualizar_ideia(id_original, mudancas):
                        alteracoes_salvas += 1
        
        if alteracoes_salvas > 0:
            st.success(f"✅ {alteracoes_salvas} ideia(s) atualizada(s) com sucesso!")
            st.rerun()  # Recarregar a página para mostrar as mudanças
        else:
            st.info("ℹ️ Nenhuma alteração detectada.")
    
    # Estatísticas rápidas
    st.subheader("📈 Estatísticas Rápidas")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_ideias = len(ideias)
        st.metric("Total de Ideias", total_ideias)
    
    with col2:
        pendentes = len([i for i in ideias if i.get('status') == 'Pendente'])
        st.metric("Pendentes", pendentes)
    
    with col3:
        aprovadas = len([i for i in ideias if i.get('status') == 'Aprovada'])
        st.metric("Aprovadas", aprovadas)
    
    with col4:
        implementadas = len([i for i in ideias if i.get('status') == 'Implementada'])
        st.metric("Implementadas", implementadas)
    
    # Ações em lote
    st.subheader("⚡ Ações em Lote")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📧 Enviar Feedback"):
            st.success("Feedback enviado para os autores selecionados!")
    
    with col2:
        if st.button("📊 Gerar Relatório"):
            # Gerar relatório em CSV
            csv_data = dados_ideias.drop('_id_completo', axis=1).to_csv(index=False)
            st.download_button(
                label="📥 Baixar Relatório CSV",
                data=csv_data,
                file_name=f"relatorio_ideias_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col3:
        if st.button("🔄 Atualizar Dados"):
            st.rerun()
    
    # Seção de detalhes da ideia selecionada
    if not dados_ideias.empty:
        st.subheader("🔍 Detalhes da Ideia")
        
        # Seletor de ideia
        opcoes_ideias = [f"{row['ID']} - {row['Título']}" for _, row in dados_ideias.iterrows()]
        ideia_selecionada = st.selectbox("Selecione uma ideia para ver detalhes:", opcoes_ideias)
        
        if ideia_selecionada:
            # Encontrar a ideia selecionada
            index_selecionado = opcoes_ideias.index(ideia_selecionada)
            id_completo = dados_ideias.iloc[index_selecionado]['_id_completo']
            
            # Buscar detalhes completos da ideia
            ideia_detalhada = None
            for ideia in ideias:
                if str(ideia['_id']) == id_completo:
                    ideia_detalhada = ideia
                    break
            
            if ideia_detalhada:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Título:** {ideia_detalhada.get('titulo', 'N/A')}")
                    st.write(f"**Autor:** {ideia_detalhada.get('autor', 'N/A')}")
                    st.write(f"**Categoria:** {ideia_detalhada.get('categoria', 'N/A')}")
                    st.write(f"**Status:** {ideia_detalhada.get('status', 'N/A')}")
                
                with col2:
                    st.write(f"**Prioridade:** {ideia_detalhada.get('prioridade', 'N/A')}")
                    st.write(f"**Responsável:** {ideia_detalhada.get('responsavel', 'N/A')}")
                    data_criacao = ideia_detalhada.get('data_criacao', 'N/A')
                    if isinstance(data_criacao, datetime):
                        data_criacao = data_criacao.strftime('%d/%m/%Y %H:%M')
                    st.write(f"**Data de Criação:** {data_criacao}")
                
                st.write(f"**Descrição:**")
                st.write(ideia_detalhada.get('descricao', 'Sem descrição disponível'))
                
                # Botão para deletar ideia
                if st.button("🗑️ Deletar Ideia", type="secondary", key=f"delete_{id_completo}"):
                    if st.session_state.get(f"confirm_delete_{id_completo}", False):
                        if mongo_manager.deletar_ideia(id_completo):
                            st.success("✅ Ideia deletada com sucesso!")
                            st.rerun()
                        else:
                            st.error("❌ Erro ao deletar ideia.")
                    else:
                        st.session_state[f"confirm_delete_{id_completo}"] = True
                        st.warning("⚠️ Clique novamente para confirmar a exclusão.")