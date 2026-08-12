import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from datetime import datetime

# --- CONFIGURAÇÃO ---
NOME_PLANILHA = "Secretária EBD ADTC Pereiro"
ABA_MATRICULADOS = "Relação Matriculados"
ABA_CHAMADAS = "Registro Chamadas"
ABA_OFERTAS = "Registro Ofertas"

def conectar_sheets():
    creds_dict = json.loads(st.secrets["GCP_CREDENTIALS"])
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client

def carregar_dados(aba):
    client = conectar_sheets()
    sheet = client.open(NOME_PLANILHA).worksheet(aba)
    return pd.DataFrame(sheet.get_all_records())

def salvar_linha(aba, dados_lista):
    client = conectar_sheets()
    sheet = client.open(NOME_PLANILHA).worksheet(aba)
    sheet.append_row(dados_lista)

CONGREGACOES = ["Sede", "Congregação Crioulas", "Congregação Chabocão", "Congregação Lagoa dos Marinheiros", "Congregação Melo", "Congregação Muritiba"]
SALAS = ["Adultos", "Adolescentes", "Jovens", "Maternal", "Juniores", "Primários", "Discipulados"]

st.set_page_config(page_title="Escola Bíblica - ADTC", page_icon="📖", layout="wide")
st.sidebar.image("Logo AD Pereiro.png", width=150)
menu = st.sidebar.radio("Escolha a Tela:", ["Matrícula de Alunos", "Realizar Chamada", "Relatórios"])

if menu == "Matrícula de Alunos":
    st.title("📖 Matrícula")
    nome = st.text_input("Nome Completo")
    endereco = st.text_input("Endereço")
    whatsapp = st.text_input("Whatsapp")
    cong = st.selectbox("Congregação", CONGREGACOES)
    sala = st.selectbox("Sala", SALAS)
    if st.button("Salvar Matrícula"):
        salvar_linha(ABA_MATRICULADOS, [datetime.now().strftime("%d/%m/%Y"), nome, endereco, whatsapp, cong, sala])
        st.success("Salvo no Google Sheets!")

elif menu == "Realizar Chamada":
    st.title("✅ Chamada")
    df_m = carregar_dados(ABA_MATRICULADOS)
    cong = st.selectbox("Congregação", CONGREGACOES)
    sala = st.selectbox("Sala", SALAS)
    alunos = df_m[(df_m["Congregação"] == cong) & (df_m["Sala"] == sala)]["Nome"].tolist()
    
    presencas = {a: st.checkbox(a) for a in alunos}
    visitantes = st.number_input("Visitantes", min_value=0)
    oferta = st.number_input("Oferta (R$)", format="%.2f")
    
    if st.button("Finalizar Chamada"):
        data = datetime.now().strftime("%d/%m/%Y")
        for a, pres in presencas.items():
            if pres:
                salvar_linha(ABA_CHAMADAS, [data, cong, sala, a, "Sim", "Sim", "Sim"])
        salvar_linha(ABA_OFERTAS, [data, cong, sala, visitantes, oferta])
        st.success("Dados enviados para a planilha!")

elif menu == "Relatórios":
    st.title("📊 Relatórios")
    df_c = carregar_dados(ABA_CHAMADAS)
    df_o = carregar_dados(ABA_OFERTAS)
    
    if not df_c.empty:
        st.dataframe(pd.merge(df_c.groupby("Sala").size().reset_index(name="Presentes"), 
                              df_o.groupby("Sala")[["Visitantes", "Valor Total"]].sum().reset_index(), 
                              on="Sala", how="outer"))
