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
    # Puxa os dados direto do Secret sem precisar converter JSON
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
        return pd.DataFrame(dados)
    except Exception as e:
        st.error(f"Erro ao carregar dados da aba {aba}: {e}")
        return pd.DataFrame()

def salvar_linha(aba, dados_lista):
    try:
        client = conectar_sheets()
        sheet = client.open(NOME_PLANILHA).worksheet(aba)
        sheet.append_row(dados_lista)
    except Exception as e:
        st.error(f"Erro ao salvar na aba {aba}: {e}")

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
        if nome:
            salvar_linha(ABA_MATRICULADOS, [datetime.now().strftime("%d/%m/%Y"), nome, endereco, whatsapp, cong, sala])
            st.success("Salvo no Google Sheets com sucesso!")
        else:
            st.warning("Preencha o nome do aluno.")

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
        st.markdown("### 👥 Lista de Alunos")
        presencas = {a: st.checkbox(a) for a in alunos}
        
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
            data = datetime.now().strftime("%d/%m/%Y")
            
            # Salva presença individual
            for a, pres in presencas.items():
                if pres:
                    salvar_linha(ABA_CHAMADAS, [data, cong, sala, a, "Sim"])
            
            # Salva totais da sala
            salvar_linha(ABA_OFERTAS, [data, cong, sala, visitantes, qtd_biblias, qtd_revistas, oferta])
            st.success("Dados da chamada e totais da sala enviados para a planilha!")

elif menu == "Relatórios":
    st.title("📊 Relatórios")
    df_c = carregar_dados(ABA_CHAMADAS)
    df_o = carregar_dados(ABA_OFERTAS)
    
    if not df_c.empty or not df_o.empty:
        pres_resumo = df_c.groupby("Sala").size().reset_index(name="Presentes") if not df_c.empty and "Sala" in df_c.columns else pd.DataFrame(columns=["Sala", "Presentes"])
        
        # Puxa visitantes, bíblias, revistas e ofertas para somar
        colunas_soma = ["Visitantes", "Bíblias", "Revistas", "Valor Total"]
        
        # Confere se as colunas já existem na planilha para não dar erro
        colunas_presentes = [col for col in colunas_soma if not df_o.empty and col in df_o.columns]
        
        if colunas_presentes:
            oferta_resumo = df_o.groupby("Sala")[colunas_presentes].sum().reset_index()
        else:
            oferta_resumo = pd.DataFrame(columns=["Sala"] + colunas_soma)
        
        relatorio_final = pd.merge(pres_resumo, oferta_resumo, on="Sala", how="outer").fillna(0)
        
        # Converte para número inteiro (remove casas decimais de quantidades)
        for col in ["Presentes", "Visitantes", "Bíblias", "Revistas"]:
            if col in relatorio_final.columns:
                relatorio_final[col] = relatorio_final[col].astype(int)
                
        st.dataframe(relatorio_final, use_container_width=True)
    else:
        st.info("Ainda não há dados suficientes nas planilhas para gerar o relatório.")
