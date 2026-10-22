# Dashboard de Cotações de Moedas

Trabalho acadêmico em Python que consulta uma API pública, realiza ETL e apresenta um dashboard em Streamlit para dólar (USD), euro (EUR) e libra esterlina (GBP), sempre em relação ao real (BRL).

## Objetivo

Analisar a evolução das cotações e comparar maior valor, menor valor, média e mediana no período selecionado. O projeto segue a divisão em arquivos do exemplo Coinbase utilizado em sala.

## Tecnologias

Python 3.12 recomendado; Requests para HTTP; Pandas para análise; SQLite para persistência; Streamlit para interface. O SQLite já acompanha o Python.

## Estrutura

| Arquivo | Responsabilidade |
|---|---|
| `api_moedas.py` | Consulta o histórico da AwesomeAPI |
| `coleta.py` | Executa extração, transformação e carga |
| `banco.py` | Cria a tabela, salva e lê os dados |
| `app.py` | Apresenta filtros, indicadores, gráficos e DataFrame |
| `requirements.txt` | Declara as dependências |
| `.gitignore` | Exclui ambiente virtual, banco gerado e arquivos locais do Git |

`cotacoes.db` será criado automaticamente. Não está incluído no projeto nem deve ser enviado ao GitHub. Nenhum dado fictício acompanha o trabalho.

## Executar no Windows com VS Code

Extraia o ZIP e abra a pasta `cotacoes_moedas` no VS Code. No terminal dessa pasta, execute uma linha de cada vez:

```powershell
py -3.12 -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m streamlit run app.py
```

Se não tiver Python 3.12, use `py -m venv venv` com uma versão compatível instalada. Os comandos usam diretamente o Python do ambiente virtual, sem exigir ativação ou alteração da política do PowerShell.

Abra o endereço mostrado pelo Streamlit, geralmente `http://localhost:8501`. Clique em **Coletar / atualizar dados**. Depois escolha moeda, compra ou venda e o período. Para encerrar o servidor, pressione `Ctrl+C` no terminal.

### Coleta pelo terminal (opcional)

```powershell
.\venv\Scripts\python.exe coleta.py
```

A coleta faz uma consulta por moeda e termina; não existe laço contínuo. Depois abra ou recarregue o dashboard. Se apenas uma moeda falhar, as demais podem ser salvas e o erro é informado.

### Linux e macOS

```bash
python3 -m venv venv
./venv/bin/python -m pip install -r requirements.txt
./venv/bin/python -m streamlit run app.py
```

## API pública utilizada

Documentação: https://docs.awesomeapi.com.br/api-de-moedas

Exemplo de solicitação:

```text
https://economia.awesomeapi.com.br/json/daily/USD-BRL/30
```

O projeto solicita até 30 registros diários de cada par: `USD-BRL`, `EUR-BRL` e `GBP-BRL`. O provedor pode retornar menos registros; não presumimos que sejam 30 dias corridos completos. A API pode impor limites ou alterar as condições de acesso. Esta versão usa consultas sem chave. Em caso de erro, o aplicativo informa a falha e mantém os dados que já estavam no banco.

## Como funciona o ETL

1. **Extract (extração):** `requests.get` consulta o endpoint HTTP; a resposta JSON contém as cotações.
2. **Transform (transformação):** converte `bid` (compra) e `ask` (venda) de texto para números, valida valores positivos e finitos e converte `timestamp` para uma data no horário de Brasília (UTC−3).
3. **Load (carga):** grava no SQLite. A chave composta por moeda e data evita duplicações. Uma nova cotação do mesmo dia atualiza o registro se seu timestamp for igual ou mais recente.

A tabela contém `moeda`, `data`, `compra`, `venda` e `instante`. A apresentação considera um registro por moeda e dia. Coletas sucessivas preservam o histórico anterior.

## Indicadores e interpretação

Todos os indicadores usam a moeda, o tipo de cotação e as datas selecionadas:

- **Mais recente no período:** último registro disponível no recorte.
- **Maior e menor cotação:** máximo e mínimo da série diária selecionada; não são máximas e mínimas intradiárias.
- **Média:** soma das cotações dividida pela quantidade de registros.
- **Mediana:** valor central dos dados ordenados; com quantidade par, média dos dois valores centrais.

Os gráficos mostram a evolução da moeda selecionada e a comparação das três em reais. O DataFrame apresenta os registros e permite exportação CSV.

Datas sem registros não são preenchidas. Não atribuímos valor zero a dias ausentes. O registro mais recente pode estar em formação. Os valores não incluem impostos, tarifas ou spread cobrado por uma instituição ao cliente e não constituem uma oferta de câmbio. As séries disponíveis não devem ser descritas como dados ao vivo ou fechamento oficial do Banco Central.

## Publicar no GitHub

Crie na sua conta um repositório vazio chamado `dashboard-cotacoes-moedas`, sem marcar criação de README, licença ou `.gitignore`, pois esta pasta já tem os arquivos necessários. Abra o Git Bash dentro da pasta do projeto:

```bash
git init
git add .
git status
```

Confira a lista: o código e o README devem aparecer; `venv/` e `cotacoes.db` não devem aparecer como novos arquivos para commit. Depois execute:

```bash
git commit -m "Adiciona dashboard de cotacoes com ETL e Streamlit"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/dashboard-cotacoes-moedas.git
git push -u origin main
```

Substitua `SEU_USUARIO` pelo seu usuário do GitHub antes de executar. O Git poderá pedir autenticação pelo navegador. Se a pasta já estiver em um repositório ou já tiver um remoto `origin`, consulte `git status` e `git remote -v` antes de adicionar outro remoto.

Para alterações futuras:

```bash
git add .
git commit -m "Atualiza o trabalho"
git push
```

Subir o código ao GitHub não publica automaticamente o dashboard como site. Quem clonar o projeto instala as dependências e coleta os dados seguindo este README.

## Roteiro de apresentação

Explique o objetivo, mostre uma chamada à API em `api_moedas.py`, demonstre as conversões em `coleta.py` e o armazenamento em `banco.py`. No painel, faça uma coleta, altere os filtros e explique a diferença entre média e mediana. Finalize mostrando o DataFrame e o repositório.

## Possíveis erros

- **Python não encontrado:** confira a instalação com `py --version`.
- **Módulo não encontrado:** instale os requisitos com o mesmo Python usado para iniciar o painel.
- **Sem dados:** clique no botão de coleta e confira os avisos.
- **Timeout, HTTP 403 ou 429:** verifique a conexão e os limites do provedor; aguarde antes de repetir. Não há consultas automáticas em sequência infinita.

## Limitações

Esta é uma versão acadêmica dedicada a três moedas. Não inclui ações da bolsa, login, investimentos ou atualização contínua. As dependências têm faixas de versão, não um lockfile exato; valide a instalação no computador usado para apresentar.
