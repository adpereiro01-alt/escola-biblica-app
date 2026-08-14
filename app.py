import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from streamlit_option_menu import option_menu
import base64
import os

# --- CONFIGURAÇÃO ---
NOME_PLANILHA = "Secretária EBD ADTC Pereiro"
ABA_MATRICULADOS = "Relação Matriculados"
ABA_PROFESSORES = "Relação Professores"
ABA_CHAMADAS = "Registro Chamadas"
ABA_OFERTAS = "Registro Ofertas"

CONGREGACOES = ["Sede", "Congregação Crioulas", "Congregação Chabocão", "Congregação Lagoa dos Marinheiros", "Congregação Melo", "Congregação Muritiba"]
SALAS = ["Adultos", "Adolescentes", "Jovens", "Maternal", "Juniores", "Primários", "Discipulados"]
TRIMESTRES = ["1º Trimestre", "2º Trimestre", "3º Trimestre", "4º Trimestre"]

def conectar_sheets():
    creds_dict = dict(st.secrets["gcp"])
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client

def carregar_dados(aba):
    try:
        client = conectar_sheets()
        sheet = client.open(NOME_PLANILHA).worksheet(aba)
        dados = sheet.get_all_records()
        if not dados:
            return pd.DataFrame()
        df = pd.DataFrame(dados)
        df["Linha_Planilha"] = df.index + 2 
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados da aba {aba}: {e}")
        return pd.DataFrame()

def salvar_linha(aba, dados_lista):
    try:
        client = conectar_sheets()
        sheet = client.open(NOME_PLANILHA).worksheet(aba)
        sheet.append_row(dados_lista)
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")

def atualizar_linha(aba, row_index, dados_lista):
    try:
        client = conectar_sheets()
        sheet = client.open(NOME_PLANILHA).worksheet(aba)
        letras = "ABCDEFGH"
        ultima_letra = letras[len(dados_lista)-1]
        cell_list = sheet.range(f'A{row_index}:{ultima_letra}{row_index}')
        for i, val in enumerate(dados_lista):
            cell_list[i].value = val
        sheet.update_cells(cell_list)
    except Exception as e:
        st.error(f"Erro ao atualizar: {e}")

# NOVA FUNÇÃO PARA EXCLUIR ALUNO OU PROFESSOR DA PLANILHA
def excluir_linha(aba, row_index):
    try:
        client = conectar_sheets()
        sheet = client.open(NOME_PLANILHA).worksheet(aba)
        sheet.delete_rows(row_index)
    except Exception as e:
        st.error(f"Erro ao excluir: {e}")

def obter_trimestre(data_str):
    try:
        mes = int(data_str.split('/')[1])
        if mes <= 3: return "1º Trimestre"
        elif mes <= 6: return "2º Trimestre"
        elif mes <= 9: return "3º Trimestre"
        else: return "4º Trimestre"
    except:
        return "1º Trimestre"

def adicionar_fundo(nome_arquivo):
    if os.path.exists(nome_arquivo):
        with open(nome_arquivo, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url(data:image/jpeg;base64,{encoded_string});
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            .block-container {{
                background-color: rgba(255, 255, 255, 0.90);
                padding: 2rem;
                border-radius: 15px;
                margin-top: 10px;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

# --- CONFIGURAÇÃO DE PÁGINA ---
st.set_page_config(page_title="Escola Bíblica - ADTC", page_icon="📖", layout="wide")

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    if os.path.exists("Logo AD Pereiro H.png"):
        st.image("Logo AD Pereiro H.png", use_container_width=True)
    
    st.markdown("---")
    
    menu = option_menu(
        menu_title="Menu Principal",
        # Nome da tela alterado para Consultar Cadastros
        options=["Início", "Cadastrar Aluno", "Cadastrar Professor", "Consultar Cadastros", "Realizar Chamada", "Relatórios"],
        icons=["house", "person-add", "easel", "search", "card-checklist", "bar-chart"], 
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#ff6600", "font-size": "18px"},
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"5px 0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#ff6600", "color": "white"},
        }
    )

# --- CABEÇALHO PARA PÁGINAS INTERNAS ---
if menu != "Início":
    col_logo_peq, col_titulo = st.columns([1, 4])
    with col_logo_peq:
        if os.path.exists("Logo AD Pereiro H.png"):
            st.image("Logo AD Pereiro H.png", use_container_width=True)
    with col_titulo:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("## Sistema de Controle de EBD")
    st.markdown("---")

# --- TELAS ---
if menu == "Início":
    adicionar_fundo("fundo_home.jpg") 
    
    col_vazia1, col_logo_centro, col_vazia2 = st.columns([1, 2, 1])
    with col_logo_centro:
        if os.path.exists("Logo AD Pereiro H.png"):
            st.image("Logo AD Pereiro H.png", use_container_width=True)
    
    st.markdown("<h1 style='text-align: center;'>Bem-vindo à Escola Bíblica Dominical</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #555;'>Assembleia de Deus Templo Central - Pereiro-CE</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 18px;'>A Escola Bíblica Dominical é o coração da nossa igreja. Aqui estudamos a Palavra de Deus, formamos o caráter cristão e fortalecemos nossa fé através de um ensino dedicado e inspirado.</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("<h3 style='text-align: center;'>Nossa Liderança</h3>", unsafe_allow_html=True)
    
    col_pastor, col_super = st.columns(2)
    with col_pastor:
        if os.path.exists("pastor.jpg"):
            st.image("pastor.jpg", width=250, caption="Pastor Presidente")
        else:
            st.info("📌 Envie a foto 'pastor.jpg' no GitHub para aparecer aqui.")
            
    with col_super:
        if os.path.exists("superintendente.jpg"):
            st.image("superintendente.jpg", width=250, caption="Superintendente da EBD")
        else:
            st.info("📌 Envie a foto 'superintendente.jpg' no GitHub para aparecer aqui.")

elif menu == "Cadastrar Aluno":
    adicionar_fundo("fundo_aluno.jpg")
    st.title("👨‍🎓 Cadastro de Aluno")
    nome = st.text_input("Nome Completo do Aluno")
    whatsapp = st.text_input("Whatsapp")
    trimestre = st.selectbox("Trimestre", TRIMESTRES)
    cong = st.selectbox("Congregação", CONGREGACOES)
    sala = st.selectbox("Sala", SALAS)
    
    if st.button("Salvar Aluno"):
        if nome:
            salvar_linha(ABA_MATRICULADOS, [datetime.now().strftime("%d/%m/%Y"), nome, whatsapp, cong, sala, trimestre])
            st.success("Aluno salvo com sucesso!")
        else:
            st.warning("Preencha o nome do aluno.")

elif menu == "Cadastrar Professor":
    adicionar_fundo("fundo_prof.jpg")
    st.title("👨‍🏫 Cadastro de Professor")
    nome = st.text_input("Nome Completo do Professor")
    whatsapp = st.text_input("Whatsapp")
    cong = st.selectbox("Congregação", CONGREGACOES)
    sala = st.selectbox("Sala", SALAS)
    
    if st.button("Salvar Professor"):
        if nome:
            salvar_linha(ABA_PROFESSORES, [datetime.now().strftime("%d/%m/%Y"), nome, whatsapp, cong, sala])
            st.success("Professor salvo com sucesso!")
        else:
            st.warning("Preencha o nome do professor.")

# --- TELA REFORMULADA: CONSULTAR CADASTROS (COM EXCLUSÃO E EDIÇÃO) ---
elif menu == "Consultar Cadastros":
    adicionar_fundo("fundo_home.jpg")
    st.title("🔍 Consultar Cadastros")
    
    tipo_edicao = st.radio("O que você deseja buscar?", ["Aluno", "Professor"], horizontal=True)
    
    aba_alvo = ABA_MATRICULADOS if tipo_edicao == "Aluno" else ABA_PROFESSORES
    df = carregar_dados(aba_alvo)
    
    if df.empty:
        st.info(f"Nenhum {tipo_edicao.lower()} encontrado.")
    else:
        col_filtro1, col_filtro2 = st.columns(2)
        with col_filtro1:
            filtro_cong = st.selectbox("Filtrar Congregação:", ["Todas"] + CONGREGACOES)
        with col_filtro2:
            filtro_sala = st.selectbox("Filtrar Sala:", ["Todas"] + SALAS)
        
        df_filtrado = df.copy()
        if filtro_cong != "Todas":
            df_filtrado = df_filtrado[df_filtrado["Congregação"] == filtro_cong]
        if filtro_sala != "Todas":
            df_filtrado = df_filtrado[df_filtrado["Sala"] == filtro_sala]
            
        if df_filtrado.empty:
            st.warning("Ninguém encontrado com esses filtros.")
        else:
            pessoa_selecionada = st.selectbox(f"Selecione o {tipo_edicao.lower()}:", df_filtrado["Nome"].tolist())
            
            dados_pessoa = df_filtrado[df_filtrado["Nome"] == pessoa_selecionada].iloc[0]
            linha_planilha = int(dados_pessoa["Linha_Planilha"])
            whats_atual = str(dados_pessoa.get("Whatsapp", "")) if "Whatsapp" in dados_pessoa else str(dados_pessoa.get("Telefone", ""))
            
            st.markdown("---")
            st.markdown(f"### 👤 {pessoa_selecionada}")
            
            # Exibe as informações como um "cartão de perfil"
            c1, c2, c3 = st.columns(3)
            c1.write(f"**📱 WhatsApp:** {whats_atual if whats_atual else 'Não informado'}")
            c2.write(f"**📍 Congregação:** {dados_pessoa.get('Congregação', '')}")
            c3.write(f"**🚪 Sala:** {dados_pessoa.get('Sala', '')}")
            
            if tipo_edicao == "Aluno":
                st.write(f"**📅 Trimestre Matriculado:** {dados_pessoa.get('Trimestre', '')}")
                
            st.markdown("<br>", unsafe_allow_html=True)
            
            # --- BOTÕES DE AÇÃO: EDITAR E EXCLUIR ---
            col_btn1, col_btn2 = st.columns([1, 1])
            
            with col_btn1:
                # O Expander funciona como uma "gaveta" que abre e fecha para editar
                with st.expander("✏️ Editar Cadastro"):
                    with st.form("form_edicao"):
                        e_nome = st.text_input("Nome", dados_pessoa.get("Nome", ""))
                        e_whatsapp = st.text_input("Whatsapp/Telefone", whats_atual)
                        
                        try: idx_cong = CONGREGACOES.index(dados_pessoa.get("Congregação", "Sede"))
                        except: idx_cong = 0
                        e_cong = st.selectbox("Congregação", CONGREGACOES, index=idx_cong)
                        
                        try: idx_sala = SALAS.index(dados_pessoa.get("Sala", "Adultos"))
                        except: idx_sala = 0
                        e_sala = st.selectbox("Sala", SALAS, index=idx_sala)
                        
                        if tipo_edicao == "Aluno":
                            try: idx_trim = TRIMESTRES.index(dados_pessoa.get("Trimestre", "1º Trimestre"))
                            except: idx_trim = 0
                            e_trimestre = st.selectbox("Trimestre", TRIMESTRES, index=idx_trim)
                        
                        if st.form_submit_button("💾 Salvar Alterações"):
                            data_original = str(dados_pessoa.get("Data", datetime.now().strftime("%d/%m/%Y")))
                            if tipo_edicao == "Aluno":
                                nova_lista = [data_original, e_nome, e_whatsapp, e_cong, e_sala, e_trimestre]
                            else:
                                nova_lista = [data_original, e_nome, e_whatsapp, e_cong, e_sala]
                                
                            atualizar_linha(aba_alvo, linha_planilha, nova_lista)
                            st.success("✅ Dados atualizados com sucesso no Google Sheets! Atualize a página para ver.")
                            
            with col_btn2:
                # Botão de exclusão (type="primary" deixa ele em destaque)
                if st.button("🗑️ Excluir Cadastro", type="primary"):
                    excluir_linha(aba_alvo, linha_planilha)
                    st.success(f"{pessoa_selecionada} excluído(a) com sucesso!")
                    st.rerun() # Atualiza a tela imediatamente para o nome sumir da lista

elif menu == "Realizar Chamada":
    adicionar_fundo("fundo_chamada.jpg")
    st.title("✅ Chamada")
    df_alunos = carregar_dados(ABA_MATRICULADOS)
    df_prof = carregar_dados(ABA_PROFESSORES)
    
    cong = st.selectbox("Congregação", CONGREGACOES)
    sala = st.selectbox("Sala", SALAS)
    
    alunos_sala = []
    if not df_alunos.empty and "Congregação" in df_alunos.columns and "Sala" in df_alunos.columns:
        alunos_sala = df_alunos[(df_alunos["Congregação"] == cong) & (df_alunos["Sala"] == sala)]["Nome"].tolist()
        
    profs_sala = []
    if not df_prof.empty and "Congregação" in df_prof.columns and "Sala" in df_prof.columns:
        profs_sala = df_prof[(df_prof["Congregação"] == cong) & (df_prof["Sala"] == sala)]["Nome"].tolist()
    
    st.markdown("### 👨‍🏫 Professor do Dia")
    if profs_sala:
        prof_dia = st.selectbox("Selecione o professor desta sala:", profs_sala + ["Outro (Substituto)"])
        if prof_dia == "Outro (Substituto)":
            prof_dia = st.text_input("Digite o nome do professor substituto:")
    else:
        st.warning("Nenhum professor cadastrado para esta sala/congregação.")
        prof_dia = st.text_input("Digite o nome do Professor:")
    
    st.markdown("### 👥 Alunos Presentes")
    if alunos_sala:
        presencas = {a: st.checkbox(a) for a in alunos_sala}
    else:
        st.info("Nenhum aluno cadastrado nesta sala.")
        presencas = {}
        
    st.markdown("---")
    st.markdown("### 📊 Fechamento da Sala")
    col1, col2 = st.columns(2)
    with col1:
        qtd_biblias = st.number_input("Quantidade de Bíblias", min_value=0)
        qtd_revistas = st.number_input("Quantidade de Revistas", min_value=0)
    with col2:
        visitantes = st.number_input("Visitantes", min_value=0)
        oferta = st.number_input("Oferta (R$)", format="%.2f")
        
    if st.button("Finalizar Chamada"):
        if not prof_dia:
            st.error("Informe quem foi o professor do dia.")
        else:
            data = datetime.now().strftime("%d/%m/%Y")
            for a, pres in presencas.items():
                if pres:
                    salvar_linha(ABA_CHAMADAS, [data, cong, sala, a, "Sim"])
            
            salvar_linha(ABA_OFERTAS, [data, cong, sala, prof_dia, visitantes, qtd_biblias, qtd_revistas, oferta])
            st.success("Chamada salva com sucesso!")

elif menu == "Relatórios":
    adicionar_fundo("fundo_relatorio.jpg")
    st.title("📊 Relatórios e Estatísticas")
    df_c = carregar_dados(ABA_CHAMADAS)
    df_o = carregar_dados(ABA_OFERTAS)
    
    if not df_c.empty or not df_o.empty:
        if not df_c.empty and "Data" in df_c.columns:
            df_c["Trimestre"] = df_c["Data"].astype(str).apply(obter_trimestre)
        if not df_o.empty and "Data" in df_o.columns:
            df_o["Trimestre"] = df_o["Data"].astype(str).apply(obter_trimestre)
            
        aba_escolhida = st.radio("Filtrar por:", ["Visão Geral", "Trimestre", "Dia Específico"], horizontal=True)
        st.markdown("---")
        
        titulo_destaque = "🏆 Destaques Gerais (Todas as Datas)"
        
        if aba_escolhida == "Trimestre":
            trim_escolhido = st.selectbox("Selecione:", TRIMESTRES)
            if not df_c.empty: df_c = df_c[df_c["Trimestre"] == trim_escolhido]
            if not df_o.empty: df_o = df_o[df_o["Trimestre"] == trim_escolhido]
            titulo_destaque = f"🏆 Destaques do {trim_escolhido}"
            
        elif aba_escolhida == "Dia Específico":
            todas_datas = set()
            if not df_c.empty: todas_datas.update(df_c["Data"].astype(str).unique())
            if not df_o.empty: todas_datas.update(df_o["Data"].astype(str).unique())
            todas_datas = sorted([d for d in todas_datas if d.strip()], reverse=True)
            
            if todas_datas:
                data_filtro = st.selectbox("Selecione a Data:", todas_datas)
                if not df_c.empty: df_c = df_c[df_c["Data"].astype(str) == data_filtro]
                if not df_o.empty: df_o = df_o[df_o["Data"].astype(str) == data_filtro]
                titulo_destaque = f"🏆 Destaques do Dia: {data_filtro}"
            else:
                st.warning("Nenhuma data encontrada nas planilhas.")
        
        st.markdown(f"### {titulo_destaque}")
        
        maior_presenca = maior_biblia = maior_revista = maior_oferta = "-"
        
        if not df_c.empty and "Sala" in df_c.columns:
            p = df_c.groupby("Sala").size()
            if not p.empty: maior_presenca = f"{p.idxmax()} ({p.max()} al.)"
                
        if not df_o.empty and "Sala" in df_o.columns:
            if "Bíblias" in df_o.columns:
                b = df_o.groupby("Sala")["Bíblias"].sum()
                if not b.empty and b.max() > 0: maior_biblia = f"{b.idxmax()} ({int(b.max())})"
            
            if "Revistas" in df_o.columns:
                r = df_o.groupby("Sala")["Revistas"].sum()
                if not r.empty and r.max() > 0: maior_revista = f"{r.idxmax()} ({int(r.max())})"
            
            if "Valor Total" in df_o.columns:
                df_o['Valor Total'] = pd.to_numeric(df_o['Valor Total'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
                o = df_o.groupby("Sala")["Valor Total"].sum()
                if not o.empty and o.max() > 0: maior_oferta = f"{o.idxmax()} (R$ {o.max():.2f})"
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🥇 Maior Presença", maior_presenca)
        c2.metric("📖 Mais Bíblias", maior_biblia)
        c3.metric("📚 Mais Revistas", maior_revista)
        c4.metric("💰 Maior Oferta", maior_oferta)
        
        st.markdown("---")
        if not df_o.empty and "Professor" in df_o.columns:
            st.markdown("### 👨‍🏫 Ranking de Professores")
            rk = df_o["Professor"].value_counts().reset_index()
            rk.columns = ["Professor", "Aulas Ministradas"]
            rk.index = range(1, len(rk) + 1)
            st.dataframe(rk, use_container_width=True)
            st.markdown("---")
        
        st.markdown("### 📋 Resumo por Sala")
        pres_resumo = df_c.groupby("Sala").size().reset_index(name="Presentes") if not df_c.empty and "Sala" in df_c.columns else pd.DataFrame(columns=["Sala", "Presentes"])
        col_soma = ["Visitantes", "Bíblias", "Revistas", "Valor Total"]
        col_pres = [c for c in col_soma if not df_o.empty and c in df_o.columns]
        
        oferta_resumo = df_o.groupby("Sala")[col_pres].sum().reset_index() if col_pres else pd.DataFrame(columns=["Sala"] + col_soma)
        rel_final = pd.merge(pres_resumo, oferta_resumo, on="Sala", how="outer").fillna(0)
        
        for col in ["Presentes", "Visitantes", "Bíblias", "Revistas"]:
            if col in rel_final.columns:
                rel_final[col] = rel_final[col].astype(int)
                
        st.dataframe(rel_final, use_container_width=True)
    else:
        st.info("Sem dados suficientes para relatórios.")
