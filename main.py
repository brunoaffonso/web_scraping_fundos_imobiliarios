import requests
from bs4 import BeautifulSoup
import locale

from tabulate import tabulate

from modelos import FundoImobiliario, Estrategia

locale.setlocale(locale.LC_ALL, 'pt_BR.UTP-8')


def trata_porcentagem(porcentagem_str):
    return locale.atof(porcentagem_str.split('%')[0])


def trata_decimal(decimal_str):
    return locale.atof(decimal_str)


headers = {'User-Agent': 'Mozilla/5.0'}

request = requests.get('https://fundamentus.com.br/fii_resultado.php', headers=headers)

soup = BeautifulSoup(request.text, 'html.parser')

lines = soup.find(id='tabelaResultado').find('tbody').find_all('tr')

result = []

estrategia = Estrategia(
    cotacao_atual_minima=50.0,
    dividend_yield_minimo=5,
    p_vp_minimo=0.70,
    valor_mercado_minimo=100000000,
    liquidez_minima=50000,
    qt_minima_imoveis=5,
    maxima_vacancia_media=10
)

for line in lines:
    dados_fundo = line.find_all('td')
    codigo = dados_fundo[0].text
    segmento = dados_fundo[1].text
    cotacao_atual = trata_decimal(dados_fundo[2].text)
    ffo_yield = trata_porcentagem(dados_fundo[3].text)
    dividend_yield = trata_porcentagem(dados_fundo[4].text)
    p_vp = trata_decimal(dados_fundo[5].text)
    valor_mercado = trata_decimal(dados_fundo[6].text)
    liquidez = trata_decimal(dados_fundo[7].text)
    qtd_imoveis = int(dados_fundo[8].text)
    preco_m2 = trata_decimal(dados_fundo[9].text)
    aluguel_m2 = trata_decimal(dados_fundo[10].text)
    cap_rate = trata_porcentagem(dados_fundo[11].text)
    vacancia_media = trata_porcentagem(dados_fundo[12].text)

    fundo_imobiliario = FundoImobiliario(
        codigo, segmento, cotacao_atual, ffo_yield, dividend_yield, p_vp, valor_mercado, liquidez,
        qtd_imoveis, preco_m2, aluguel_m2, cap_rate, vacancia_media
    )

    if estrategia.aplica_estrategia(fundo_imobiliario):
        result.append(fundo_imobiliario)


header = ['CÓDIGO', 'SEGMENTO', 'COTAÇÃO ATUAL', 'DIVIDEND YIELD']

table = []

for elemento in result:
    table.append([
        elemento.codigo,
        elemento.segmento,
        locale.currency(elemento.cotacao_atual),
        f'{locale.str(elemento.dividend_yield)} %'
    ])

print(tabulate(table, headers=header, showindex='always', tablefmt='fancy_grid'))
