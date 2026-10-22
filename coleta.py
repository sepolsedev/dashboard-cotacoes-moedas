"""ETL: extrair da API, transformar e carregar no SQLite."""
from datetime import datetime, timezone, timedelta
import math
from api_moedas import MOEDAS, consultar_historico
from banco import criar_tabela, salvar_cotacoes

# Horário de Brasília; os timestamps da API representam instantes em UTC.
BRASILIA = timezone(timedelta(hours=-3))


def transformar_dados(moeda, dados):
    registros = []
    for item in dados:
        # Valores da API são textos; convertemos antes de armazenar e analisar.
        compra = float(item["bid"])
        venda = float(item["ask"])
        instante = int(item["timestamp"])
        if not all(math.isfinite(v) and v > 0 for v in (compra, venda)):
            raise ValueError("Cotação inválida recebida da API.")
        data = datetime.fromtimestamp(instante, BRASILIA).date().isoformat()
        registros.append((moeda, data, compra, venda, instante))
    return registros


def executar_coleta():
    criar_tabela()
    resultados = []
    # Uma falha em uma moeda não impede a coleta das demais.
    for moeda, nome in MOEDAS.items():
        try:
            dados = consultar_historico(moeda, dias=30)
            registros = transformar_dados(moeda, dados)
            salvar_cotacoes(registros)
            resultados.append((True, f"{nome}: {len(registros)} registros processados."))
        except Exception as erro:
            resultados.append((False, f"{nome}: falha na coleta ({erro})."))
    return resultados


if __name__ == "__main__":
    resultados = executar_coleta()
    for sucesso, mensagem in resultados:
        print(("OK: " if sucesso else "ERRO: ") + mensagem)
    # Código de saída indica falha, mesmo que parte dos dados tenha sido salva.
    raise SystemExit(0 if all(ok for ok, _ in resultados) else 1)
