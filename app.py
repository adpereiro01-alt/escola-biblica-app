import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- CONFIGURAÇÃO ---
NOME_PLANILHA = "Secretária EBD ADTC Pereiro"
ABA_MATRICULADOS = "Relação Matriculados"
ABA_PROFESSORES = "Relação Professores" # Nova Aba
ABA_CHAMADAS = "Registro Chamadas"
ABA_OFERTAS = "Registro Ofertas"

# ... (funções conectar_sheets, carregar_dados, salvar_linha, atualizar_linha permanecem iguais) ...

# (Dica: garanta que as funções de conexão e leitura estejam presentes no topo como antes)

st.set_page_config(page_title="Escola Bíblica - ADTC", page_icon="📖", layout="wide")
menu = st.sidebar.radio("Menu:", ["Cadastrar Aluno", "Cadastrar Professor", "Consultar Matrículas", "Realizar Chamada", "Relatórios"])

if menu == "Cadastrar Aluno":
    st.title("👨‍🎓 Cadastro de Aluno")
    nome = st.text_input("Nome do Aluno")
    cong = st.selectbox("Congregação", CONGREGACOES)
    sala = st.selectbox("Sala", SALAS)
    if st.button("Salvar Aluno"):
        salvar_linha(ABA_MATRICULADOS, [datetime.now().strftime("%d/%m/%Y"), nome, cong, sala])
        st.success("Aluno salvo!")

elif menu == "Cadastrar Professor":
    st.title("👨‍🏫 Cadastro de Professor")
    nome = st.text_input("Nome do Professor")
    cong = st.selectbox("Congregação", CONGREGACOES)
    sala = st.selectbox("Sala", SALAS)
    if st.button("Salvar Professor"):
        salvar_linha(ABA_PROFESSORES, [datetime.now().strftime("%d/%m/%Y"), nome, cong, sala])
        st.success("Professor salvo!")

elif menu == "Realizar Chamada":
    st.title("✅ Chamada")
    # Carrega ambos
    df_alunos = carregar_dados(ABA_MATRICULADOS)
    df_prof = carregar_dados(ABA_PROFESSORES)
    
    cong = st.selectbox("Congregação", CONGREGACOES)
    sala = st.selectbox("Sala", SALAS)
    
    # Filtra apenas quem é daquela sala e congregação
    alunos_sala = df_alunos[(df_alunos["Congregação"] == cong) & (df_alunos["Sala"] == sala)]["Nome"].tolist()
    profs_sala = df_prof[(df_prof["Congregação"] == cong) & (df_prof["Sala"] == sala)]["Nome"].tolist()
    
    st.markdown("### 👨‍🏫 Professor do Dia")
    prof_dia = st.selectbox("Selecione o Professor:", profs_sala + ["Outro"])
    
    st.markdown("### 👥 Alunos Presentes")
    presencas = {a: st.checkbox(a) for a in alunos_sala}
    
    # ... (restante do fechamento igual)
