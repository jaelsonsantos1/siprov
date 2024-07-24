# Siprov

Siprov é um projeto de automação para extração de dados da plataforma Siprov. Utilizando Python, o projeto realiza login na plataforma, gera relatórios de forma automatizada e extrai as informações necessárias para análise de dados com PowerBI.

## Índice

- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
- [Tecnologias](#tecnologias)
- [Contribuição](#contribuição)
- [Licença](#licença)

## Instalação

Para começar a usar o Siprov, siga os passos abaixo:

1. Clone este repositório:
    ```bash
    git clone https://github.com/seuusuario/siprov.git
    ```

2. Navegue até o diretório do projeto:
    ```bash
    cd siprov
    ```

3. Crie um ambiente virtual:
    ```bash
    python -m venv venv
    ```

4. Ative o ambiente virtual:
    - No Windows:
      ```bash
      venv\Scripts\activate
      ```
    - No macOS e Linux:
      ```bash
      source venv/bin/activate
      ```

5. Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

## Configuração

Antes de executar o projeto, você precisa configurar suas credenciais de acesso à plataforma Siprov e as preferências de relatório. Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

```
URL_BASE = "https://acesso.siprov.com.br/siprov-web/"
USER="XXXXXXXXXXX"
PASS="XXXXXXXXXXX"
```

## Uso

Após configurar suas credenciais, você pode executar o script principal para iniciar a extração de dados:

```bash
python scraping.py
```

O script irá:

1. Realizar login na plataforma Siprov.
2. Gerar o relatório especificado.
3. Extrair os dados do relatório.
4. Salvar os dados em um formato adequado para análise no PowerBI.

## Tecnologias

O projeto Siprov utiliza as seguintes tecnologias:

- **Python**: Linguagem de programação principal do projeto.
- **aiohttp**: Biblioteca para realizar requisições HTTP de forma assíncrona.
- **BeautifulSoup**: Biblioteca para parsing de HTML.
- **lxml**: Biblioteca para parsing e modificação de XML e HTML.
- **dotenv**: Biblioteca para carregar variáveis de ambiente de um arquivo `.env`.

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
