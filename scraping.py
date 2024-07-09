"""SCript de rapasgem de dados do site siprov.com.br."""

import asyncio
from bs4 import BeautifulSoup as bs
import pandas as pd
import aiohttp

#  Constantes
URL_BASE = "https://acesso.siprov.com.br/siprov-web/"
LOGIN = "jbprotecaoveicular.adm@gmail.com"
PASSWORD = "Site*123456"

def get_viewstate(html):
    """Pegar o viewstate da página."""
    soup = bs(html, 'html.parser')
    return soup.find('input', id='j_id1:javax.faces.ViewState:0').get('value')

async def do_login(session):
    """Fazer o login no acesso.siprov.com.br."""
    response = await session.get(URL_BASE+"login.jsf")
    html = await response.text()
    viewstate_login = get_viewstate(html)
    payload = {
        'javax.faces.partial.ajax': 'true',
        'javax.faces.source': 'btnAcessar',
        'javax.faces.partial.execute': 'painelLogin',
        'javax.faces.partial.render': 'frmLogin painelMascaras',
        'btnAcessar': 'btnAcessar',
        'frmLogin': 'frmLogin',
        'email1': LOGIN,
        'senha1': PASSWORD,
        'painelGuias_activeIndex': '0',
        'javax.faces.ViewState': viewstate_login
    }
    return await session.post(URL_BASE+"login.jsf", data=payload)

async def to_load(session, endpoint):
    """Carregar o último relatório criado."""
    print("Carregando o último relatório criado...")
    new_url = URL_BASE+endpoint

    response = await session.get(new_url)
    html = await response.text()
    soup = bs(html, 'html.parser')

    last_id = [
        id['id'] for id in soup.find_all('a', class_='ui-commandlink')
    ]

    if last_id == []:
        return None
    else:
        last_id = last_id[0]

    viewstate = get_viewstate(html)
    payload = {
        'frmPrincipal': 'frmPrincipal',
        'javax.faces.ViewState': viewstate,
        f'{last_id}': f'{last_id}'
    }

    res_data = await session.post(new_url, data=payload)
    res_content = await res_data.content.read()


    # Relatório carregado
    dataframe = pd.read_excel(res_content, engine='openpyxl')
    return dataframe

# Gerar o relatório de cobranças
async def generate_report(session):
    """Gerar o relatório de cobranças."""
    print("Gerando o relatório de cobranças...")
    response = await session.get(URL_BASE +
                                 'app/relatorio/relatorioPersonalizadoFinanceiroEdit.jsf')
    html = await response.text()

    viewstate = viewstate = get_viewstate(html)
    payload = {
        'javax.faces.partial.ajax': 'true',
        'javax.faces.source': 'btnExportar',
        'javax.faces.partial.execute': 'frmPrincipal',
        'javax.faces.partial.render': 'frmPrincipal painelMascaras',
        'btnExportar': 'btnExportar',
        'frmPrincipal': 'frmPrincipal',
        'j_idt218': 'CREDITO',
        'j_idt223_input': '364',
        'j_idt227': 'XLSX',
        'j_idt244': '0',
        'j_idt287_input': '01/01/2024',
        'j_idt289_input': '31/12/2024',
        'j_idt318': [
            'ABERTO',
            'PENDENTE',
            'CANCELADO',
            'LIQUIDADO',
        ],
        'javax.faces.ViewState': viewstate
    }

    return await session.post(URL_BASE +
                              'app/relatorio/relatorioPersonalizadoFinanceiroEdit.jsf',
                              data=payload)

async def main():
    """Função principal."""
    async with aiohttp.ClientSession() as session:
        await do_login(session)

        await asyncio.sleep(5)

        await generate_report(session)
        await asyncio.sleep(450)
        return await to_load(session, 'app/relatorio/relatorioPersonalizadoFinanceiroList.jsf')

if __name__ == '__main__':
    df = asyncio.run(main())
    print(df)
    print("Script finalizado com sucesso.")
