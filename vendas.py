"""SCript de rapasgem de dados do site siprov.com.br."""

import asyncio
from bs4 import BeautifulSoup as bs
import pandas as pd
import aiohttp
import os
from dotenv import load_dotenv
from lxml import etree
from io import BytesIO
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module='openpyxl')

load_dotenv()

#  Constantes
url_siprov = os.getenv("URL_BASE")
login_siprov = os.getenv("USER")
password_siprov = os.getenv("PASS")

def get_viewstate(response_content):
    """Pegar o viewstate da página."""
    soup = bs(response_content, 'html.parser')
    viewstate = soup.find('input', {'name': 'javax.faces.ViewState'})['value']
    return viewstate

async def do_login(session):
    """Fazer o login no acesso.siprov.com.br."""
    async with session.get(url_siprov + "login.jsf") as response:
        response_content = await response.text()

    viewstate = get_viewstate(response_content)

    payload = {
        'javax.faces.partial.ajax': 'true',
        'javax.faces.source': 'btnAcessar',
        'javax.faces.partial.execute': 'painelLogin',
        'javax.faces.partial.render': 'frmLogin painelMascaras',
        'btnAcessar': 'btnAcessar',
        'frmLogin': 'frmLogin',
        'email1': login_siprov,
        'senha1': password_siprov,
        'painelGuias_activeIndex': '0',
        'javax.faces.ViewState': viewstate
    }

    async with session.post(url_siprov + "login.jsf", data=payload) as response:
        await response.text()

    await asyncio.sleep(2)
    print("Login efetuado com sucesso.")

    return

def get_element_id(html, xpath):
    """Captura o 'id' de um elemento dado o HTML e o XPath."""
    element = html.xpath(xpath)
    if element:
        return element[0].get('id')
    return None

def format_payload(page):
    """Formatar o payload para o relatório."""
    soup = bs(page, 'html.parser')
    html = etree.HTML(str(soup))

    viewstate = get_viewstate(page)

    # Tipo de Lançamento
    input_release_type_id = get_element_id(html, "/html/body/div[1]/div[4]/div[1]/div/div/form/div/div/div/div[2]/table/tbody/tr[1]/td[2]/table/tbody/tr/td[1]/div/div[2]/select")
    # Laiaute
    input_layout_id = get_element_id(html, "/html/body/div[1]/div[4]/div[1]/div/div/form/div/div/div/div[2]/table/tbody/tr[1]/td[2]/table/tbody/tr/td[1]/div/div[2]/select")
    # Data de emissão inicial
    input_start_date_id = get_element_id(html, "/html/body/div[1]/div[4]/div[1]/div/div/form/div/div/div/div[2]/table/tbody/tr[9]/td[2]/table/tbody/tr/td[1]/span/input")
    # Data de emissão final
    input_end_date_id = get_element_id(html, "/html/body/div[1]/div[4]/div[1]/div/div/form/div/div/div/div[2]/table/tbody/tr[9]/td[2]/table/tbody/tr/td[3]/span/input")
    # Natureza do Associado
    input_client_nature_id = get_element_id(html, "/html/body/div[1]/div[4]/div[1]/div/div/form/div/div/div/div[2]/table/tbody/tr[7]/td[2]/table")
    # Títulos Financeiros
    input_titles_finance_id = get_element_id(html, "/html/body/div[1]/div[4]/div[1]/div/div/form/div/div/div/div[2]/table/tbody/tr[22]/td[2]/table")
    # Tipo associado
    input_associated_type_id = get_element_id(html, "/html/body/div[1]/div[4]/div[1]/div/div/form/div/div/div/div[2]/table/tbody/tr[20]/td[2]/table")
    # Formato da exportação
    input_format_type_id = get_element_id(html, "/html/body/div[1]/div[4]/div[1]/div/div/form/div/div/div/div[2]/table/tbody/tr[1]/td[2]/table/tbody/tr/td[3]/table")

    payload = {
        'javax.faces.partial.ajax': 'true',
        'javax.faces.source': 'btnExportar',
        'javax.faces.partial.execute': 'frmPrincipal',
        'javax.faces.partial.render': 'frmPrincipal painelMascaras',
        'btnExportar': 'btnExportar',
        'frmPrincipal': 'frmPrincipal',
        f'{input_release_type_id}': 'CREDITO',
        f'{input_layout_id}': '1393',
        f'{input_format_type_id}': 'XLSX',
        f'{input_client_nature_id}': '0',
        f'{input_start_date_id}': '01/01/2024',
        f'{input_end_date_id}': '31/12/2024',
        f'{input_titles_finance_id}': '0',
        f'{input_associated_type_id}': '0',
        'javax.faces.ViewState': viewstate
    }

    return payload

async def generate_report(session):
    """Gerar o relatório de cobranças."""
    async with session.get(url_siprov + 'app/relatorio/relatorioPersonalizadoAdesaoEdit.jsf') as response:
        response_content = await response.text()
    
    payload_formated = format_payload(response_content)

    async with session.post(url_siprov + 'app/relatorio/relatorioPersonalizadoAdesaoEdit.jsf',data=payload_formated) as response:
        await response.text()

    print("Relatório gerado com sucesso.")

async def to_load(session, endpoint):
    """Carregar o último relatório criado."""
    async with session.get(url_siprov + endpoint) as res_data:
        page_content = await res_data.text()
    
    soup = bs(page_content, 'html.parser')

    last_id = [
        id['id'] for id in soup.find_all('a', class_='ui-commandlink')
    ]

    if last_id == []:
        return None
    else:
        last_id = last_id[0]

    viewstate = get_viewstate(page_content)
    payload = {
        'frmPrincipal': 'frmPrincipal',
        'javax.faces.ViewState': viewstate,
        f'{last_id}': f'{last_id}'
    }

    async with session.post(url_siprov + endpoint, data=payload) as res_data:
        res_content = await res_data.content.read()
        excel_data = BytesIO(res_content)
        dataframe = pd.read_excel(excel_data, engine='openpyxl')
        print("Relatório carregado com sucesso.")
        
        return dataframe

async def main():
    """Função principal."""
    async with aiohttp.ClientSession() as session:
        await do_login(session)
        await generate_report(session)
        await asyncio.sleep(5)
        return await to_load(session, 'app/relatorio/relatorioPersonalizadoFinanceiroList.jsf')

if __name__ == '__main__':
    df = asyncio.run(main())
