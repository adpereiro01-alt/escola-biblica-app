import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- CONFIGURAÇÃO ---
NOME_PLANILHA = "Secretária EBD ADTC Pereiro"
ABA_MATRICULADOS = "Relação Matriculados"
ABA_CHAMADAS = "Registro Chamadas"
ABA_OFERTAS = "Registro Ofertas"

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
        cell_list = sheet.range(f'A{row_index}:H{row_index}')
        for i, val in enumerate(dados_lista):
            cell_list[i].value = val
        sheet.update_cells(cell_list)
    except Exception as e:
        st.error(f"Erro ao atualizar: {e}")

def obter_trimestre(data_str):
    try:
        mes = int(data_str.split('/')[1])
        if mes <= 3: return "1º Trimestre"
        elif mes <= 6: return "2º Trimestre"
        elif mes <= 9: return "3º Trimestre"
        else: return "4º Trimestre"
    except:
        return "1º Trimestre"

CONGREGACOES = ["Sede", "Congregação Crioulas", "Congregação Chabocão", "Congregação Lagoa dos Marinheiros", "Congregação Melo", "Congregação Muritiba"]
SALAS = ["Adultos", "Adolescentes", "Jovens", "Maternal", "Juniores", "Primários", "Discipulados"]
TRIMESTRES = ["1º Trimestre", "2º Trimestre", "3º Trimestre", "4º Trimestre"]

st.set_page_config(page_title="Escola Bíblica - ADTC", page_icon="📖", layout="wide")
st.sidebar.image("Logo AD Pereiro.png", width=150)
menu = st.sidebar.radio("Escolha a Tela:", ["Matrícula", "Consultar/Editar Matrículas", "Realizar Chamada", "Relatórios"])

if menu == "Matrícula":
    st.title("📖 Nova Matrícula")
    
    col1, col2 = st.columns(2)
    with col1:
        cargo = st.radio("Cargo:", ["Aluno", "Professor"], horizontal=True)
        nome = st.text_input("Nome Completo")
        whatsapp = st.text_input("Whatsapp")
    with col2:
        trimestre = st.selectbox("Trimestre de Entrada:", TRIMESTRES)
        cong = st.selectbox("Congregação", CONGREGACOES)
        sala = st.selectbox("Sala", SALAS)
    
    endereco = st.text_input("Endereço")
    
    if st.button("Salvar Cadastro"):
        if nome:
            salvar_linha(ABA_MATRICULADOS, [datetime.now().strftime("%d/%m/%Y"), nome, endereco, whatsapp, cong, sala, cargo, trimestre])
            st.success(f"{cargo} salvo no Google Sheets com sucesso!")
        else:
            st.warning("Preencha o nome.")

elif menu == "Consultar/Editar Matrículas":
    st.title("🔍 Consultar e Editar Matrículas")
    df_m = carregar_dados(ABA_MATRICULADOS)
    
    if df_m.empty:
        st.info("Nenhuma matrícula encontrada.")
    else:
        col_filtro1, col_filtro2 = st.columns(2)
        with col_filtro1:
            filtro_cong = st.selectbox("Filtrar Congregação:", ["Todas"] + CONGREGACOES)
        with col_filtro2:
            filtro_sala = st.selectbox("Filtrar Sala:", ["Todas"] + SALAS)
        
        df_filtrado = df_m.copy()
        if filtro_cong != "Todas":
            df_filtrado = df_filtrado[df_filtrado["Congregação"] == filtro_cong]
        if filtro_sala != "Todas":
            df_filtrado = df_filtrado[df_filtrado["Sala"] == filtro_sala]
            
        if df_filtrado.empty:
            st.warning("Ninguém encontrado com esses filtros.")
        else:
            pessoa_selecionada = st.selectbox("Selecione a pessoa para editar:", df_filtrado["Nome"].tolist())
            
            dados_pessoa = df_filtrado[df_filtrado["Nome"] == pessoa_selecionada].iloc[0]
            linha_planilha = int(dados_pessoa["Linha_Planilha"])
            
            st.markdown("---")
            st.markdown(f"### ✏️ Editando: {pessoa_selecionada}")
            
            with st.form("form_edicao"):
                e_nome = st.text_input("Nome", dados_pessoa.get("Nome", ""))
                e_whatsapp = st.text_input("Whatsapp", str(dados_pessoa.get("Whatsapp", "")))
                e_endereco = st.text_input("Endereço", str(dados_pessoa.get("Endereço", "")))
                
                try: idx_cong = CONGREGACOES.index(dados_pessoa.get("Congregação", "Sede"))
                except: idx_cong = 0
                e_cong = st.selectbox("Congregação", CONGREGACOES, index=idx_cong)
                
                try: idx_sala = SALAS.index(dados_pessoa.get("Sala", "Adultos"))
                except: idx_sala = 0
                e_sala = st.selectbox("Sala", SALAS, index=idx_sala)
                
                e_cargo = st.radio("Cargo", ["Aluno", "Professor"], index=0 if dados_pessoa.get("Cargo", "Aluno") == "Aluno" else 1, horizontal=True)
                
                try: idx_trim = TRIMESTRES.index(dados_pessoa.get("Trimestre", "1º Trimestre"))
                except: idx_trim = 0
                e_trimestre = st.selectbox("Trimestre", TRIMESTRES, index=idx_trim)
                
                if st.form_submit_button("💾 Salvar Alterações"):
                    data_original = str(dados_pessoa.get("Data", datetime.now().strftime("%d/%m/%Y")))
                    nova_lista = [data_original, e_nome, e_endereco, e_whatsapp, e_cong, e_sala, e_cargo, e_trimestre]
                    atualizar_linha(ABA_MATRICULADOS, linha_planilha, nova_lista)
                    st.success("Dados atualizados com sucesso! Atualize a página para ver as mudanças.")

elif menu == "Realizar Chamada":
    st.title("✅ Chamada")
    df_m = carregar_dados(ABA_MATRICULADOS)
    cong = st.selectbox("Congregação", CONGREGACOES)
    sala = st.selectbox("Sala", SALAS)
    
    if not df_m.empty and "Congregação" in df_m.columns and "Sala" in df_m.columns:
        if "Cargo" not in df_m.columns:
            df_m["Cargo"] = "Aluno"
            
        alunos = df_m[(df_m["Congregação"] == cong) & (df_m["Sala"] == sala) & (df_m["Cargo"] == "Aluno")]["Nome"].tolist()
        professores = df_m[(df_m["Congregação"] == cong) & (df_m["Sala"] == sala) & (df_m["Cargo"] == "Professor")]["Nome"].tolist()
    else:
        alunos = []
        professores = []
        
    if not alunos and not professores:
        st.info("Nenhum cadastro encontrado para esta congregação/sala.")
    else:
        st.markdown("### 👨‍🏫 Professor do Dia")
        if professores:
            prof_dia = st.selectbox("Selecione quem deu a aula hoje:", professores + ["Outro (Substituto)"])
            if prof_dia == "Outro (Substituto)":
                prof_dia = st.text_input("Digite o nome do substituto:")
        else:
            st.warning("Nenhum professor cadastrado para esta sala.")
            prof_dia = st.text_input("Digite o nome do Professor que deu a aula:")
        
        st.markdown("### 👥 Lista de Alunos")
        if alunos:
            presencas = {a: st.checkbox(a) for a in alunos}
        else:
            st.info("Apenas professores cadastrados. Nenhum aluno nesta sala.")
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
                st.error("Por favor, informe quem foi o professor do dia.")
            else:
                data = datetime.now().strftime("%d/%m/%Y")
                for a, pres in presencas.items():
                    if pres:
                        salvar_linha(ABA_CHAMADAS, [data, cong, sala, a, "Sim"])
                
                salvar_linha(ABA_OFERTAS, [data, cong, sala, prof_dia, visitantes, qtd_biblias, qtd_revistas, oferta])
                st.success("Chamada e totais enviados com sucesso!")

elif menu == "Relatórios":
    st.title("📊 Relatórios e Estatísticas")
    df_c = carregar_dados(ABA_CHAMADAS)
    df_o = carregar_dados(ABA_OFERTAS)
    
    if not df_c.empty or not df_o.empty:
        if not df_c.empty and "Data" in df_c.columns:
            df_c["Trimestre"] = df_c["Data"].astype(str).apply(obter_trimestre)
        if not df_o.empty and "Data" in df_o.columns:
            df_o["Trimestre"] = df_o["Data"].astype(str).apply(obter_trimestre)
            
        aba_escolhida = st.radio("O que deseja ver?", ["Visão Geral", "Filtrar por Trimestre", "Filtrar por Dia Específico"], horizontal=True)
        st.markdown("---")
        
        if aba_escolhida == "Filtrar por Trimestre":
            trim_escolhido = st.selectbox("Selecione o Trimestre:", TRIMESTRES)
            if not df_c.empty: df_c = df_c[df_c["Trimestre"] == trim_escolhido]
            if not df_o.empty: df_o = df_o[df_o["Trimestre"] == trim_escolhido]
            
        elif aba_escolhida == "Filtrar por Dia Específico":
            todas_datas = set()
            if not df_c.empty: todas_datas.update(df_c["Data"].astype(str).unique())
            if not df_o.empty: todas_datas.update(df_o["Data"].astype(str).unique())
            todas_datas = sorted([d for d in todas_datas if d.strip()], reverse=True)
            
            data_filtro = st.selectbox("📅 Selecione a Data:", todas_datas)
            if not df_c.empty: df_c = df_c[df_c["Data"].astype(str) == data_filtro]
            if not df_o.empty: df_o = df_o[df_o["Data"].astype(str) == data_filtro]
        
        st.markdown("### 🏆 Destaques do Período Selecionado")
        maior_presenca = "-"
        maior_biblia = "-"
        maior_revista = "-"
        maior_oferta = "-"
        
        if not df_c.empty and "Sala" in df_c.columns:
            presencas_por_sala = df_c.groupby("Sala").size()
            if not presencas_por_sala.empty:
                maior_presenca = f"{presencas_por_sala.idxmax()} ({presencas_por_sala.max()} al.)"
                
        if not df_o.empty and "Sala" in df_o.columns:
            if "Bíblias" in df_o.columns:
                bib_por_sala = df_o.groupby("Sala")["Bíblias"].sum()
                if not bib_por_sala.empty and bib_por_sala.max() > 0:
                    maior_biblia = f"{bib_por_sala.idxmax()} ({int(bib_por_sala.max())})"
            
            if "Revistas" in df_o.columns:
                rev_por_sala = df_o.groupby("Sala")["Revistas"].sum()
                if not rev_por_sala.empty and rev_por_sala.max() > 0:
                    maior_revista = f"{rev_por_sala.idxmax()} ({int(rev_por_sala.max())})"
                    
            if "Valor Total" in df_o.columns:
                of_por_sala = df_o.groupby("Sala")["Valor Total"].sum()
                if not of_por_sala.empty and of_por_sala.max() > 0:
                    maior_oferta = f"{of_por_sala.idxmax()} (R$ {of_por_sala.max():.2f})"
        
        col_est1, col_est2, col_est3, col_est4 = st.columns(4)
        col_est1.metric("🥇 Maior Presença", maior_presenca)
        col_est2.metric("📖 Mais Bíblias", maior_biblia)
        col_est3.metric("📚 Mais Revistas", maior_revista)
        col_est4.metric("💰 Maior Oferta", maior_oferta)
        
        st.markdown("---")
        
        # RANKING DE PROFESSORES
        if not df_o.empty and "Professor" in df_o.columns:
            st.markdown("### 👨‍🏫 Ranking de Professores (Aulas Ministradas)")
            ranking_prof = df_o["Professor"].value_counts().reset_index()
            ranking_prof.columns = ["Professor", "Quantidade de Aulas"]
            ranking_prof.index = range(1, len(ranking_prof) + 1) # Começa o ranking do 1
            st.dataframe(ranking_prof, use_container_width=True)
            st.markdown("---")
        
        # TABELA GERAL
        st.markdown("### 📋 Resumo por Sala")
        pres_resumo = df_c.groupby("Sala").size().reset_index(name="Presentes") if not df_c.empty and "Sala" in df_c.columns else pd.DataFrame(columns=["Sala", "Presentes"])
        colunas_soma = ["Visitantes", "Bíblias", "Revistas", "Valor Total"]
        colunas_presentes = [col for col in colunas_soma if not df_o.empty and col in df_o.columns]
        
        if colunas_presentes:
            oferta_resumo = df_o.groupby("Sala")[colunas_presentes].sum().reset_index()
        else:
            oferta_resumo = pd.DataFrame(columns=["Sala"] + colunas_soma)
        
        relatorio_final = pd.merge(pres_resumo, oferta_resumo, on="Sala", how="outer").fillna(0)
        for col in ["Presentes", "Visitantes", "Bíblias", "Revistas"]:
            if col in relatorio_final.columns:
                relatorio_final[col] = relatorio_final[col].astype(int)
                
        st.dataframe(relatorio_final, use_container_width=True)
    else:
        st.info("Ainda não há dados suficientes nas planilhas para gerar o relatório.")
