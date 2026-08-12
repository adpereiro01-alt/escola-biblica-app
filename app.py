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
    
    # Garante que as quebras de linha da chave privada sejam interpretadas corretamente
    if "private_key" in creds_dict:
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client

def carregar_dados(aba):
    client = conectar_sheets()
    sheet = client.open(NOME_PLANILHA).worksheet(aba)
    dados = sheet.get_all_records()
    if not dados:
        return pd.DataFrame()
    return pd.DataFrame(dados)

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
        st.success("Salvo no Google Sheets com sucesso!")

elif menu == "Realizar Chamada":
    st.title("✅ Chamada")
    df_m = carregar_dados(ABA_MATRICULADOS)
    cong = st.selectbox("Congregação", CONGREGACOES)
    sala = st.selectbox("Sala", SALAS)
    
    if not df_m.empty and "Congregação" in df_m.columns and "Sala" in df_m.columns:
        alunos = df_m[(df_m["Congregação"] == cong) & (df_m["Sala"] == sala)]["Nome"].tolist()
    else:
        alunos = []
        
    if not alunos:
        st.info("Nenhum aluno cadastrado para esta congregação/sala.")
    else:
        presencas = {a: st.checkbox(a) for a in alunos}
        visitantes = st.number_input("Visitantes", min_value=0)
        oferta = st.number_input("Oferta (R$)", format="%.2f")
        
        if st.button("Finalizar Chamada"):
            data = datetime.now().strftime("%d/%m/%Y")
            for a, pres in presencas.items():
                if pres:
                    salvar_linha(ABA_CHAMADAS, [data, cong, sala, a, "Sim", "Sim", "Sim"])
            salvar_linha(ABA_OFERTAS, [data, cong, sala, visitantes, oferta])
            st.success("Dados da chamada enviados para a planilha!")

elif menu == "Relatórios":
    st.title("📊 Relatórios")
    df_c = carregar_dados(ABA_CHAMADAS)
    df_o = carregar_dados(ABA_OFERTAS)
    
    if not df_c.empty or not df_o.empty:
        # Exibição segura dos dados unidos
        pres_resumo = df_c.groupby("Sala").size().reset_index(name="Presentes") if not df_c.empty else pd.DataFrame(columns=["Sala", "Presentes"])
        oferta_resumo = df_o.groupby("Sala")[["Visitantes", "Valor Total"]].sum().reset_index() if not df_o.empty else pd.DataFrame(columns=["Sala", "Visitantes", "Valor Total"])
        
        relatorio_final = pd.merge(pres_resumo, oferta_resumo, on="Sala", how="outer").fillna(0)
        st.dataframe(relatorio_final, use_container_width=True)
    else:
        st.info("Ainda não há dados suficientes nas planilhas para gerar o relatório.")
