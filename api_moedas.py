"""Extração: comunicação com a API pública de cotações."""
import requests

MOEDAS = {"USD-BRL": "Dólar", "EUR-BRL": "Euro", "GBP-BRL": "Libra"}


def consultar_historico(moeda, dias=30):
    """Solicita até 30 registros diários. O provedor pode retornar menos."""
    if moeda not in MOEDAS:
        raise ValueError("Moeda não suportada.")
    resposta = requests.get(
        f"https://economia.awesomeapi.com.br/json/daily/{moeda}/{dias}",
        timeout=30,
    )
    resposta.raise_for_status()  # Identifica erros HTTP, como limite de acesso.
    dados = resposta.json()
    if not isinstance(dados, list) or not dados:
        raise ValueError("A API não retornou uma lista de cotações.")
    return dados
