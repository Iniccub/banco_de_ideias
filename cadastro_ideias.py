import streamlit as st
from mongodb_connection import mongo_manager
from datetime import datetime
import uuid

def criar_formulario_ideia():
    st.header("💡 Cadastrar Nova Ideia")
    
    with st.form("formulario_ideia"):
        col1, col2 = st.columns(2)
        
        with col1:
            titulo = st.text_input("Título da Ideia*", placeholder="Digite o título da sua ideia")
            autor = st.text_input("Seu Nome*", placeholder="Digite seu nome")
            email = st.text_input("E-mail", placeholder="seu.email@exemplo.com")
            
        with col2:
            categoria = st.selectbox(
                "Categoria*",
                [
                    "Tecnologia & Inovação",
                    "Currículo & Metodologia", 
                    "Infraestrutura",
                    "Bem Estar",
                    "Eventos",
                    "Sustentabilidade",
                    "Outros"
                ]
            )
            
            prioridade = st.selectbox(
                "Prioridade",
                ["Baixa", "Média", "Alta", "Crítica"]
            )
            
            impacto = st.selectbox(
                "Impacto Esperado",
                ["Baixo", "Médio", "Alto", "Muito Alto"]
            )
        
        # Descrição da ideia
        descricao = st.text_area(
            "Descrição da Ideia*",
            placeholder="Descreva sua ideia detalhadamente...",
            height=150
        )
        
        # Justificativa
        justificativa = st.text_area(
            "Justificativa",
            placeholder="Por que esta ideia é importante?",
            height=100
        )
        
        # Recursos necessários
        recursos = st.text_area(
            "Recursos Necessários",
            placeholder="Quais recursos serão necessários para implementar?",
            height=100
        )
        
        # Benefícios esperados
        beneficios = st.text_area(
            "Benefícios Esperados",
            placeholder="Quais benefícios esta ideia trará?",
            height=100
        )
        
        # Prazo estimado
        col3, col4 = st.columns(2)
        with col3:
            prazo_implementacao = st.selectbox(
                "Prazo para Implementação",
                ["1-3 meses", "3-6 meses", "6-12 meses", "Mais de 1 ano"]
            )
        
        with col4:
            orcamento_estimado = st.selectbox(
                "Orçamento Estimado",
                ["Até R$ 1.000", "R$ 1.000 - R$ 5.000", "R$ 5.000 - R$ 10.000", "Acima de R$ 10.000"]
            )
        
        # Tags
        tags = st.text_input(
            "Tags (separadas por vírgula)",
            placeholder="inovação, educação, tecnologia"
        )
        
        submitted = st.form_submit_button("💾 Salvar Ideia", use_container_width=True)
        
        if submitted:
            # Validação
            if not titulo or not autor or not descricao:
                st.error("⚠️ Por favor, preencha todos os campos obrigatórios (*)")
                return
            
            # Preparar dados para salvar
            ideia_data = {
                "id_unico": str(uuid.uuid4()),
                "titulo": titulo,
                "autor": autor,
                "email": email,
                "categoria": categoria,
                "prioridade": prioridade,
                "impacto": impacto,
                "descricao": descricao,
                "justificativa": justificativa,
                "recursos": recursos,
                "beneficios": beneficios,
                "prazo_implementacao": prazo_implementacao,
                "orcamento_estimado": orcamento_estimado,
                "tags": [tag.strip() for tag in tags.split(",") if tag.strip()],
                "status": "Pendente",
                "votos": 0,
                "comentarios": [],
                "data_submissao": datetime.now().isoformat()
            }
            
            # Salvar no MongoDB
            with st.spinner("Salvando ideia..."):
                ideia_id = mongo_manager.salvar_ideia(ideia_data)
                
                if ideia_id:
                    st.success(f"✅ Ideia salva com sucesso! ID: {ideia_id}")
                    st.balloons()
                    
                    # Mostrar resumo
                    with st.expander("📋 Resumo da Ideia Cadastrada"):
                        st.write(f"**Título:** {titulo}")
                        st.write(f"**Autor:** {autor}")
                        st.write(f"**Categoria:** {categoria}")
                        st.write(f"**Prioridade:** {prioridade}")
                        st.write(f"**Descrição:** {descricao}")
                else:
                    st.error("❌ Erro ao salvar a ideia. Tente novamente.")

def listar_ideias():
    st.header("📋 Ideias Cadastradas")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filtro_categoria = st.selectbox(
            "Filtrar por Categoria",
            ["Todas", "Tecnologia & Inovação", "Currículo & Metodologia", 
             "Infraestrutura", "Bem Estar", "Eventos", "Sustentabilidade", "Outros"]
        )
    
    with col2:
        filtro_status = st.selectbox(
            "Filtrar por Status",
            ["Todos", "Pendente", "Em Análise", "Aprovada", "Implementada", "Rejeitada"]
        )
    
    with col3:
        ordenacao = st.selectbox(
            "Ordenar por",
            ["Data (Mais Recente)", "Data (Mais Antiga)", "Título", "Autor", "Votos"]
        )
    
    # Buscar ideias
    filtros = {}
    if filtro_categoria != "Todas":
        filtros["categoria"] = filtro_categoria
    if filtro_status != "Todos":
        filtros["status"] = filtro_status
    
    ideias = mongo_manager.buscar_ideias(filtros)
    
    if not ideias:
        st.info("📭 Nenhuma ideia encontrada com os filtros selecionados.")
        return
    
    # Exibir estatísticas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Ideias", len(ideias))
    with col2:
        total_votos = sum(ideia.get('votos', 0) for ideia in ideias)
        st.metric("Total de Votos", total_votos)
    with col3:
        aprovadas = len([i for i in ideias if i.get('status') == 'Aprovada'])
        st.metric("Aprovadas", aprovadas)
    with col4:
        implementadas = len([i for i in ideias if i.get('status') == 'Implementada'])
        st.metric("Implementadas", implementadas)
    
    # Exibir ideias
    for ideia in ideias:
        with st.expander(f"💡 {ideia.get('titulo', 'Sem título')} - {ideia.get('autor', 'Anônimo')}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Descrição:** {ideia.get('descricao', 'Sem descrição')}")
                st.write(f"**Categoria:** {ideia.get('categoria', 'Não informada')}")
                st.write(f"**Prioridade:** {ideia.get('prioridade', 'Não informada')}")
                
                if ideia.get('tags'):
                    tags_str = ", ".join(ideia['tags'])
                    st.write(f"**Tags:** {tags_str}")
            
            with col2:
                st.write(f"**Status:** {ideia.get('status', 'Pendente')}")
                st.write(f"**Curtidas:** {ideia.get('votos', 0)}")
                st.write(f"**Data:** {ideia.get('data_criacao', 'Não informada')}")
                
                # Botões de ação
                if st.button(f"👍 Curtir", key=f"votar_{ideia['_id']}"):
                    novo_total_votos = ideia.get('votos', 0) + 1
                    if mongo_manager.atualizar_ideia(str(ideia['_id']), {'votos': novo_total_votos}):
                        st.success("Voto registrado!")
                        st.rerun()