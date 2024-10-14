# importar bibliotecas
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import timedelta
import datetime
import markdown


today = datetime.datetime.now()
print("HOJE", today)

# Criar as funções de carregamento de dados
# cotaçoes
@st.cache#Armazenando em cache para nao precisar carregar tudo do site ao abrir toda vez
def carregar_dados(empresas):
    texto_tickers = " ".join(empresas)
    dados_acao = yf.Tickers(texto_tickers)
    cotacoes_acao = dados_acao.history(period="1d", start="2010-01-01", end="2024-10-14")
    cotacoes_acao = cotacoes_acao["Close"]
    return cotacoes_acao

@st.cache#Armazenando em cache para nao precisar carregar tudo do site ao abrir toda vez
def carregar_tickers_acoes():# caregando todas as empresas listadas por arquivo .csv
    base_tickers = pd.read_csv("IBOV.csv", sep=";")
    tickers = (base_tickers["Código"])
    tickers = [item + ".SA" for item in tickers]#para cada ticker adicionar o .SA

    return tickers

#Lista de acoes
acoes = carregar_tickers_acoes()

# preparar a visualização = filtros
#barra lateral
dados = carregar_dados(acoes)
st.sidebar.header("Filtros")

lista_acoes = st.sidebar.multiselect("Escolha as ações a visualizar", dados.columns)
if lista_acoes:
    dados = dados[lista_acoes]

#Filtro de datas
data_inicial = dados.index.min().to_pydatetime()
data_final = dados.index.max().to_pydatetime()
intervalo_data = st.sidebar.slider("Selecione o periodo",
                           min_value=data_inicial,
                           max_value=data_final,
                           value=(data_inicial, data_final),
                            step=timedelta(days=1))
print(intervalo_data[1])
dados = dados.loc[intervalo_data[0]:intervalo_data[1]]

# criar interface
# usando formatação markdown
st.write("""
# App Preço de Ações
O gráfico abaixo representa a evolução do preço das ações ao longo dos anos""")

#criar grafico
st.line_chart(dados)

texto_performace_ativos = ""

#caso nao tenha nenhuma ação selecionada carregar todas as ações
if len(lista_acoes)==0:
    lista_acoes = list(dados.columns)

#Simulando uma carteira com valor/peso 1000 em cada açao selecionada
carteira = [1000 for acao in lista_acoes]
total_inicial_carteira = sum(carteira)

for i, acao in enumerate(lista_acoes):#listando açao e performance
    performance_ativo = dados[acao].iloc[-1] / dados[acao].iloc[0] -1
    performance_ativo = float(performance_ativo)

    carteira[i] = carteira[i] * (1 + performance_ativo)

    if performance_ativo > 0:
        texto_performace_ativos = texto_performace_ativos + f"  \n{acao}: :green[{performance_ativo:.1%}]"
    elif performance_ativo < 0:
        texto_performace_ativos = texto_performace_ativos + f"  \n{acao}: :red[{performance_ativo:.1%}]"
    else:
        texto_performace_ativos = texto_performace_ativos + f"  \n{acao}: {performance_ativo:.1%}"

total_final_carteira = sum(carteira)
performance_carteira = total_final_carteira / total_inicial_carteira -1

if performance_carteira > 0:
    texto_performance_carteira = f"Performance da carteira com todos os ativos: :green[{performance_carteira:.1%}]"
elif performance_carteira < 0:
    texto_performance_carteira = f"Performance da carteira com todos os ativos: :red[{performance_carteira:.1%}]"
else:
    texto_performance_carteira = f"Performance da carteira com todos os ativos: {performance_carteira:.1%}"

st.write(f"""
### Preformance dos Ativos
Essa foi a performance dos ativos no periodo selecionado: 

{texto_performace_ativos}

{texto_performance_carteira}
""")