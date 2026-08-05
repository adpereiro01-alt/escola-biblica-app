import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime

ARQUIVO_MATRICULAS = "matriculas_escola_biblica.xlsx"
ARQUIVO_CHAMADAS = "chamadas_escola_biblica.xlsx"
ARQUIVO_OFERTAS = "ofertas_escola_biblica.xlsx"

# ----------------- FUNÇÕES DE BANCO DE DADOS -----------------
def carregar_dados_matricula():
    if not os.path.exists(ARQUIVO_MATRICULAS):
        df = pd.DataFrame(columns=["Data", "Nome", "Endereço", "Whatsapp", "Congregação", "Sala"])
        df.to_excel(ARQUIVO_MATRICULAS, index=False)
        return df
    return pd.read_excel(ARQUIVO_MATRICULAS)

def carregar_dados_chamada():
    if not os.path.exists(ARQUIVO_CHAMADAS):
        # Adicionada a coluna Congregação aqui também!
        df = pd.DataFrame(columns=["Data", "Congregação", "Sala", "Aluno", "Presente", "Trouxe Bíblia", "Trouxe Revista"])
        df.to_excel(ARQUIVO_CHAMADAS, index=False)
        return df
    return pd.read_excel(ARQUIVO_CHAMADAS)

def carregar_dados_ofertas():
    if not os.path.exists(ARQUIVO_OFERTAS):
        # Adicionada a coluna Congregação para o controle financeiro
        df = pd.DataFrame(columns=["Data", "Congregação", "Sala", "Valor Total"])
        df.to_excel(ARQUIVO_OFERTAS, index=False)
        return df
    return pd.read_excel(ARQUIVO_OFERTAS)

def formatar_whatsapp(numero):
    apenas_numeros = re.sub(r'\D', '', numero)
    if len(apenas_numeros) == 11:
        return f"({apenas_numeros[:2]}) {apenas_numeros[2:7]}-{apenas_numeros[7:]}"
    elif len(apenas_numeros) == 10:
        return f"({apenas_numeros[:2]}) {apenas_numeros[2:6]}-{apenas_numeros[6:]}"
    return numero

CONGREGACOES = ["Sede", "Congregação Crioulas", "Congregação Chabocão", "Congregação Lagoa dos Marinheiros", "Congregação Melo", "Congregação Muritiba"]
SALAS = ["Adultos", "Adolescentes", "Jovens", "Maternal", "Juniores", "Primários", "Discipulados"]

# ----------------- CONFIGURAÇÃO DA PÁGINA -----------------
st.set_page_config(page_title="Escola Bíblica", page_icon="📖", layout="wide")

st.sidebar.title("Navegação")
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3389/3389081.png", width=100) 

# Novo item no menu: Relatórios
menu = st.sidebar.radio("Escolha a Tela:", ["Matrícula de Alunos", "Realizar Chamada", "Relatórios"])

# ----------------- TELA 1: MATRÍCULA -----------------
if menu == "Matrícula de Alunos":
    st.title("Matrícula - Escola Bíblica")
    
    df_matriculas = carregar_dados_matricula()

    with st.form("matricula_form", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        endereco = st.text_input("Endereço")
        whatsapp = st.text_input("N. Whatsapp", placeholder="Ex: 88999999999")
        
        col1, col2 = st.columns(2)
        with col1:
            congregacao = st.selectbox("Congregação", CONGREGACOES)
        with col2:
            sala = st.selectbox("Sala", SALAS)

        if st.form_submit_button("Salvar Matrícula"):
            if nome == "":
                st.error("Por favor, digite o nome do aluno.")
            else:
                data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
                whatsapp_pronto = formatar_whatsapp(whatsapp)
                
                novo_registro = pd.DataFrame({
                    "Data": [data_atual], "Nome": [nome], "Endereço": [endereco],
                    "Whatsapp": [whatsapp_pronto], "Congregação": [congregacao], "Sala": [sala]
                })
                
                df_atualizado = pd.concat([df_matriculas, novo_registro], ignore_index=True)
                df_atualizado.to_excel(ARQUIVO_MATRICULAS, index=False)
                st.success(f"Matrícula de {nome} salva com sucesso!")

# ----------------- TELA 2: CHAMADA -----------------
elif menu == "Realizar Chamada":
    st.title("Chamada - Escola Bíblica")
    
    df_matriculas = carregar_dados_matricula()
    df_chamadas = carregar_dados_chamada()
    df_ofertas = carregar_dados_ofertas()

    if df_matriculas.empty:
        st.warning("Nenhum aluno matriculado ainda.")
    else:
        # Filtros Lado a Lado
        col1, col2 = st.columns(2)
        with col1:
            cong_selecionada = st.selectbox("1. Selecione a Congregação:", CONGREGACOES)
        with col2:
            sala_selecionada = st.selectbox("2. Selecione a Sala:", SALAS)
        
        # O Python filtra cruzando as duas informações (Congregação E Sala)
        df_sala = df_matriculas[(df_matriculas["Congregação"] == cong_selecionada) & (df_matriculas["Sala"] == sala_selecionada)]
        lista_alunos = df_sala["Nome"].tolist() 
        
        if len(lista_alunos) == 0:
            st.info(f"Nenhum aluno encontrado na sala {sala_selecionada} da {cong_selecionada}.")
        else:
            st.write("---")
            col_nome, col_presenca, col_biblia, col_revista = st.columns([3, 1, 1, 1])
            col_nome.markdown("**Nome do Aluno**")
            col_presenca.markdown("**Presente?**")
            col_biblia.markdown("**Bíblia?**")
            col_revista.markdown("**Revista?**")
            st.write("---")
            
            resultados_presenca = {}
            resultados_biblia = {}
            resultados_revista = {}

            for aluno in lista_alunos:
                c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                c1.write(aluno)
                resultados_presenca[aluno] = c2.checkbox("Sim", key=f"p_{aluno}")
                resultados_biblia[aluno] = c3.checkbox("Sim", key=f"b_{aluno}")
                resultados_revista[aluno] = c4.checkbox("Sim", key=f"r_{aluno}")
            
            st.write("---")
            
            st.subheader("Oferta da Sala")
            oferta_total = st.number_input("Valor arrecadado hoje (R$)", min_value=0.0, format="%.2f")

            if st.button("Finalizar e Salvar Tudo"):
                data_atual = datetime.now().strftime("%d/%m/%Y") 
                
                novos_registros = []
                for aluno in lista_alunos:
                    novos_registros.append({
                        "Data": data_atual,
                        "Congregação": cong_selecionada, # Salvando a congregação na chamada
                        "Sala": sala_selecionada,
                        "Aluno": aluno,
                        "Presente": "Sim" if resultados_presenca[aluno] else "Não",
                        "Trouxe Bíblia": "Sim" if resultados_biblia[aluno] else "Não",
                        "Trouxe Revista": "Sim" if resultados_revista[aluno] else "Não"
                    })
                
                df_chamadas = pd.concat([df_chamadas, pd.DataFrame(novos_registros)], ignore_index=True)
                df_chamadas.to_excel(ARQUIVO_CHAMADAS, index=False)
                
                novo_registro_oferta = pd.DataFrame({
                    "Data": [data_atual],
                    "Congregação": [cong_selecionada], # Salvando a congregação na oferta
                    "Sala": [sala_selecionada],
                    "Valor Total": [oferta_total]
                })
                df_ofertas = pd.concat([df_ofertas, novo_registro_oferta], ignore_index=True)
                df_ofertas.to_excel(ARQUIVO_OFERTAS, index=False)
                
                st.success("Dados salvos com sucesso!")

# ----------------- TELA 3: RELATÓRIOS -----------------
elif menu == "Relatórios":
    st.title("Painel de Relatórios")
    
    # Criando as abas separadas na tela
    aba1, aba2 = st.tabs(["📊 Relatório de Frequência e Material", "💰 Relatório de Ofertas"])
    
    with aba1:
        st.subheader("Histórico de Chamadas")
        df_chamadas = carregar_dados_chamada()
        if df_chamadas.empty:
            st.info("Nenhuma chamada registrada ainda.")
        else:
            st.dataframe(df_chamadas, use_container_width=True) # Mostra a planilha na tela
            
    with aba2:
        st.subheader("Histórico Financeiro das Salas")
        df_ofertas = carregar_dados_ofertas()
        if df_ofertas.empty:
            st.info("Nenhuma oferta registrada ainda.")
        else:
            st.dataframe(df_ofertas, use_container_width=True) # Mostra a planilha na tela
