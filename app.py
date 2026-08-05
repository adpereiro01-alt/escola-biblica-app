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
    apenas_numeros = re.sub(r'\D', '', str(numero))
    if len(apenas_numeros) == 11:
        return f"({apenas_numeros[:2]}) {apenas_numeros[2:7]}-{apenas_numeros[7:]}"
    elif len(apenas_numeros) == 10:
        return f"({apenas_numeros[:2]}) {apenas_numeros[2:6]}-{apenas_numeros[6:]}"
    return str(numero)

CONGREGACOES = ["Sede", "Congregação Crioulas", "Congregação Chabocão", "Congregação Lagoa dos Marinheiros", "Congregação Melo", "Congregação Muritiba"]
SALAS = ["Adultos", "Adolescentes", "Jovens", "Maternal", "Juniores", "Primários", "Discipulados"]

# ----------------- CONFIGURAÇÃO DA PÁGINA -----------------
st.set_page_config(page_title="Escola Bíblica - ADTC", page_icon="📖", layout="wide")

st.sidebar.title("Navegação")
st.sidebar.image("Logo AD Pereiro.png", width=150) # Logo inserida com sucesso

menu = st.sidebar.radio("Escolha a Tela:", ["Matrícula de Alunos", "Realizar Chamada", "Relatórios"])

# ----------------- TELA 1: MATRÍCULA -----------------
if menu == "Matrícula de Alunos":
    st.title("📖 Matrícula - Escola Bíblica")
    
    with st.expander("ℹ️ Instruções - Como cadastrar novos alunos"):
        st.markdown("""
        * Preencha o **Nome Completo** do aluno.
        * Informe o endereço e o WhatsApp (o sistema formata o número automaticamente).
        * Selecione a **Congregação** correta e a **Sala** correspondente à faixa etária ou classe do aluno.
        * Clique em **Salvar Matrícula** para registrar os dados no sistema.
        """)

    df_matriculas = carregar_dados_matricula()

    with st.form("matricula_form", clear_on_submit=True):
        nome = st.text_input("Nome Completo", help="Digite o nome completo do membro ou aluno.")
        endereco = st.text_input("Endereço", help="Rua, número e bairro (opcional).")
        whatsapp = st.text_input("N. Whatsapp", placeholder="Ex: 88999999999", help="Apenas números com DDD.")
        
        col1, col2 = st.columns(2)
        with col1:
            congregacao = st.selectbox("Congregação", CONGREGACOES, help="Selecione a congregação frequentada.")
        with col2:
            sala = st.selectbox("Sala", SALAS, help="Selecione a classe/sala de EBD.")

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
    st.title("✅ Chamada - Escola Bíblica")
    
    with st.expander("ℹ️ Instruções - Como realizar a chamada semanal"):
        st.markdown("""
        1. **Selecione a Congregação** e a **Sala** correspondente nos seletores abaixo.
        2. Para cada aluno listado, marque se ele esteve **Presente**, se trouxe a **Bíblia** e se trouxe a **Revista**.
        3. No final da página, informe a **Quantidade de Visitantes** que participaram da sala naquele dia.
        4. Digite o **Valor Total** arrecadado de ofertas daquela sala e clique em **Finalizar e Salvar Tudo**.
        """)

    df_matriculas = carregar_dados_matricula()
    df_chamadas = carregar_dados_chamada()
    df_ofertas = carregar_dados_ofertas()

    if df_matriculas.empty:
        st.warning("Nenhum aluno matriculado ainda. Vá na aba de 'Matrícula de Alunos' para cadastrar primeiro.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            cong_selecionada = st.selectbox("1. Selecione a Congregação:", CONGREGACOES)
        with col2:
            sala_selecionada = st.selectbox("2. Selecione a Sala:", SALAS)
        
        df_sala = df_matriculas[(df_matriculas["Congregação"] == cong_selecionada) & (df_matriculas["Sala"] == sala_selecionada)]
        lista_alunos = df_sala["Nome"].tolist() 
        
        if len(lista_alunos) == 0:
            st.info(f"Nenhum aluno encontrado na sala **{sala_selecionada}** da **{cong_selecionada}**. Cadastre alunos para esta sala primeiro.")
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
            
            st.subheader("💰 Informações e Oferta da Sala")
            col_inf1, col_inf2 = st.columns(2)
            with col_inf1:
                qtd_visitantes = st.number_input("Quantidade de Visitantes na Sala", min_value=0, step=1, help="Número de pessoas que visitaram a classe hoje.")
            with col_inf2:
                oferta_total = st.number_input("Valor total arrecadado (R$)", min_value=0.0, format="%.2f", help="Soma em dinheiro das ofertas da sala.")

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

# ----------------- TELA 3: RELATÓRIO UNIFICADO -----------------
elif menu == "Relatórios":
    st.title("📊 Painel de Relatório Consolidado da EBD")
    
    with st.expander("ℹ️ Instruções - Como ler e filtrar os relatórios"):
        st.markdown("""
        * **Filtro de Congregação:** Escolha uma congregação específica para ver apenas os dados dela, ou selecione **"Todas"** para ver o consolidado geral.
        * **Filtro de Data:** Escolha o dia da EBD que deseja consultar ou selecione **"Todas"** para acumular o histórico completo.
        * A tabela abaixo cruza automaticamente as chamadas com as ofertas, dividindo os dados por **Sala**.
        """)
    
    df_chamadas = carregar_dados_chamada()
    df_ofertas = carregar_dados_ofertas()

    if df_chamadas.empty and df_ofertas.empty:
        st.info("Nenhum dado de chamada ou oferta registrado ainda.")
    else:
        st.subheader("Filtros de Consulta")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filtro_cong = st.selectbox("Filtrar Congregação:", ["Todas"] + CONGREGACOES)
        with col_f2:
            todas_datas = sorted(list(set(df_chamadas["Data"].dropna().tolist() + df_ofertas["Data"].dropna().tolist())))
            filtro_data = st.selectbox("Filtrar Data:", ["Todas"] + todas_datas)

        # 1. Processando Frequência
        if not df_chamadas.empty:
            df_c_filt = df_chamadas.copy()
            if filtro_cong != "Todas":
                df_c_filt = df_c_filt[df_c_filt["Congregação"] == filtro_cong]
            if filtro_data != "Todas":
                df_c_filt = df_c_filt[df_c_filt["Data"] == filtro_data]

            df_c_filt["p_num"] = df_c_filt["Presente"].apply(lambda x: 1 if x == "Sim" else 0)
            df_c_filt["b_num"] = df_c_filt["Trouxe Bíblia"].apply(lambda x: 1 if x == "Sim" else 0)
            df_c_filt["r_num"] = df_c_filt["Trouxe Revista"].apply(lambda x: 1 if x == "Sim" else 0)

            freq_agrupada = df_c_filt.groupby("Sala").agg(
                Presentes=("p_num", "sum"),
                Bíblias=("b_num", "sum"),
                Revistas=("r_num", "sum")
            ).reset_index()
        else:
            freq_agrupada = pd.DataFrame(columns=["Sala", "Presentes", "Bíblias", "Revistas"])

        # 2. Processando Ofertas e Visitantes
        if not df_ofertas.empty:
            df_o_filt = df_ofertas.copy()
            if filtro_cong != "Todas":
                df_o_filt = df_o_filt[df_o_filt["Congregação"] == filtro_cong]
            if filtro_data != "Todas":
                df_o_filt = df_o_filt[df_o_filt["Data"] == filtro_data]

            ofertas_agrupadas = df_o_filt.groupby("Sala").agg(
                Visitantes=("Visitantes", "sum"),
                Valor_Total=("Valor Total", "sum")
            ).reset_index()
        else:
            ofertas_agrupadas = pd.DataFrame(columns=["Sala", "Visitantes", "Valor_Total"])

        # 3. Unificando
        if not freq_agrupada.empty or not ofertas_agrupadas.empty:
            relatorio_final = pd.merge(freq_agrupada, ofertas_agrupadas, on="Sala", how="outer").fillna(0)
            
            relatorio_final["Ofertas (R$)"] = relatorio_final["Valor_Total"].apply(lambda x: f"R$ {x:,.2f}")
            relatorio_final = relatorio_final.drop(columns=["Valor_Total"])

            st.markdown("---")
            st.subheader("Resumo Geral por Sala")
            st.dataframe(relatorio_final, use_container_width=True)

            # Métricas Totais
            st.markdown("### 📌 Totais Gerais")
            tot_pres = int(relatorio_final["Presentes"].sum()) if "Presentes" in relatorio_final else 0
            tot_bib = int(relatorio_final["Bíblias"].sum()) if "Bíblias" in relatorio_final else 0
            tot_rev = int(relatorio_final["Revistas"].sum()) if "Revistas" in relatorio_final else 0
            tot_vis = int(relatorio_final["Visitantes"].sum()) if "Visitantes" in relatorio_final else 0
            
            if not df_ofertas.empty and 'df_o_filt' in locals():
                val_num_tot = df_o_filt["Valor Total"].sum()
            else:
                val_num_tot = 0

            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Total Presentes", tot_pres)
            m2.metric("Total Bíblias", tot_bib)
            m3.metric("Total Revistas", tot_rev)
            m4.metric("Total Visitantes", tot_vis)
            m5.metric("Total Ofertas", f"R$ {val_num_tot:,.2f}")
        else:
            st.warning("Nenhum registro encontrado para os filtros selecionados.")
