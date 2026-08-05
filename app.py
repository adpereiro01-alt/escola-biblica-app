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
        df = pd.DataFrame(columns=["Data", "Congregação", "Sala", "Aluno", "Presente", "Trouxe Bíblia", "Trouxe Revista"])
        df.to_excel(ARQUIVO_CHAMADAS, index=False)
        return df
    return pd.read_excel(ARQUIVO_CHAMADAS)

def carregar_dados_ofertas():
    if not os.path.exists(ARQUIVO_OFERTAS):
        df = pd.DataFrame(columns=["Data", "Congregação", "Sala", "Visitantes", "Valor Total"])
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
st.set_page_config(page_title="Escola Bíblica - ADTC", page_icon="📖", layout="wide")

st.sidebar.title("Navegação")
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3389/3389081.png", width=100) 
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
        col1, col2 = st.columns(2)
        with col1:
            cong_selecionada = st.selectbox("1. Selecione a Congregação:", CONGREGACOES)
        with col2:
            sala_selecionada = st.selectbox("2. Selecione a Sala:", SALAS)
        
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
            
            st.subheader("Informações e Oferta da Sala")
            col_inf1, col_inf2 = st.columns(2)
            with col_inf1:
                # Novo campo de visitantes solicitado
                qtd_visitantes = st.number_input("Quantidade de Visitantes na Sala", min_value=0, step=1)
            with col_inf2:
                oferta_total = st.number_input("Valor total arrecadado (R$)", min_value=0.0, format="%.2f")

            if st.button("Finalizar e Salvar Tudo"):
                data_atual = datetime.now().strftime("%d/%m/%Y") 
                
                novos_registros = []
                for aluno in lista_alunos:
                    novos_registros.append({
                        "Data": data_atual,
                        "Congregação": cong_selecionada,
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
                    "Congregação": [cong_selecionada],
                    "Sala": [sala_selecionada],
                    "Visitantes": [qtd_visitantes],
                    "Valor Total": [oferta_total]
                })
                df_ofertas = pd.concat([df_ofertas, novo_registro_oferta], ignore_index=True)
                df_ofertas.to_excel(ARQUIVO_OFERTAS, index=False)
                
                st.success("Dados salvos com sucesso!")

# ----------------- TELA 3: RELATÓRIOS -----------------
elif menu == "Relatórios":
    st.title("Painel de Relatórios Consolidados")
    
    aba1, aba2 = st.tabs(["📊 Relatório Consolidado de Frequência", "💰 Relatório de Ofertas e Visitantes"])
    
    df_chamadas = carregar_dados_chamada()
    df_ofertas = carregar_dados_ofertas()

    with aba1:
        st.subheader("Filtro por Congregação e Data")
        if df_chamadas.empty:
            st.info("Nenhuma chamada registrada ainda.")
        else:
            # Filtros na tela de relatório
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                filtro_cong = st.selectbox("Filtrar Congregação:", ["Todas"] + CONGREGACOES, key="f_cong")
            with col_f2:
                datas_disponiveis = ["Todas"] + sorted(df_chamadas["Data"].unique().tolist())
                filtro_data = st.selectbox("Filtrar Data:", datas_disponiveis, key="f_data")
            
            # Aplicando os filtros no banco de dados de chamadas
            df_filtrado = df_chamadas.copy()
            if filtro_cong != "Todas":
                df_filtrado = df_filtrado[df_filtrado["Congregação"] == filtro_cong]
            if filtro_data != "Todas":
                df_filtrado = df_filtrado[df_filtrado["Data"] == filtro_data]

            if df_filtrado.empty:
                st.warning("Nenhum dado encontrado para os filtros selecionados.")
            else:
                # Transformando "Sim" e "Não" em 1 e 0 para poder somar de forma consolidada por sala
                df_filtrado["p_num"] = df_filtrado["Presente"].apply(lambda x: 1 if x == "Sim" else 0)
                df_filtrado["b_num"] = df_filtrado["Trouxe Bíblia"].apply(lambda x: 1 if x == "Sim" else 0)
                df_filtrado["r_num"] = df_filtrado["Trouxe Revista"].apply(lambda x: 1 if x == "Sim" else 0)

                # Agrupando por Sala para trazer cada sala em uma linha separada
                relatorio_consolidado = df_filtrado.groupby("Sala").agg(
                    Total_Presentes=("p_num", "sum"),
                    Total_Biblias=("b_num", "sum"),
                    Total_Revistas=("r_num", "sum")
                ).reset_index()

                st.markdown("### Resumo por Sala")
                st.dataframe(relatorio_consolidado, use_container_width=True)

    with aba2:
        st.subheader("Histórico Financeiro e de Visitantes")
        if df_ofertas.empty:
            st.info("Nenhuma oferta registrada ainda.")
        else:
            # Filtros para a aba de ofertas
            col_fo1, col_fo2 = st.columns(2)
            with col_fo1:
                filtro_cong_of = st.selectbox("Filtrar Congregação (Ofertas):", ["Todas"] + CONGREGACOES, key="f_cong_of")
            with col_fo2:
                datas_of_disp = ["Todas"] + sorted(df_ofertas["Data"].unique().tolist())
                filtro_data_of = st.selectbox("Filtrar Data (Ofertas):", datas_of_disp, key="f_data_of")

            df_of_filtrado = df_ofertas.copy()
            if filtro_cong_of != "Todas":
                df_of_filtrado = df_of_filtrado[df_of_filtrado["Congregação"] == filtro_cong_of]
            if filtro_data_of != "Todas":
                df_of_filtrado = df_of_filtrado[df_of_filtrado["Data"] == filtro_data_of]

            if df_of_filtrado.empty:
                st.warning("Nenhum registro financeiro encontrado para os filtros selecionados.")
            else:
                # Agrupando as ofertas e visitantes por sala e congregação
                relatorio_ofertas = df_of_filtrado.groupby(["Congregação", "Sala"]).agg(
                    Total_Visitantes=("Visitantes", "sum"),
                    Valor_Total_Ofertas=("Valor Total", "sum")
                ).reset_index()

                # Formatando a coluna de dinheiro para o padrão Real (R$)
                relatorio_ofertas["Valor Total de Ofertas"] = relatorio_ofertas["Valor_Total_Ofertas"].apply(lambda x: f"R$ {x:,.2f}")
                relatorio_ofertas = relatorio_ofertas.drop(columns=["Valor_Total_Ofertas"])

                st.dataframe(relatorio_ofertas, use_container_width=True)
