# RAG-IPVA — ES

Assistente tributário para IPVA do Espírito Santo com RAG e interface Streamlit.

## Pré-requisitos

- Python 3.11+
- Conta Google AI Studio (para gerar chave `GEMINI_API_KEY`) ou uso local com TF-IDF

## Configuração do ambiente

1. Crie e ative um ambiente virtual:
	```pwsh
	python -m venv .venv
	.venv\Scripts\Activate.ps1
	```
2. Instale as dependências:
	```pwsh
	pip install -r project/requirements.txt
	```
3. Copie o arquivo de exemplo de variáveis e ajuste conforme necessário:
	```pwsh
	Copy-Item project/.env.example project/.env
	```
	- Preencha `GEMINI_API_KEY` para habilitar geração/embeddings com Gemini.
	- Ajuste `EMBEDDINGS_PROVIDER=tfidf` caso prefira operar sem chave.
	- As variáveis `DATASET_DOCS_DIR`, `OUTPUT_DOCS_DIR` e `INGESTION_MANIFEST_PATH` permitem customizar os caminhos de ingestão.

## Ingestão de documentos

Processa os arquivos brutos em `dataset/data/docs` e gera versões normalizadas (com front matter) em `project/data/docs`:

```pwsh
python project/rag/ingestion.py
```

Um manifest é salvo em `project/data/ingestion_manifest.json` com os metadados consolidados.

## Indexação

Gera o índice vetorial consumido pelo engine:

```pwsh
$env:EMBEDDINGS_PROVIDER = 'tfidf'   # opcional, use 'gemini' se tiver chave
python -m rag.indexer
Remove-Item Env:EMBEDDINGS_PROVIDER -ErrorAction SilentlyContinue
```

O arquivo resultante é `project/data/index.pkl`.

### Usando embeddings Gemini

- Defina `GEMINI_API_KEY` no `.env` ou na sessão atual (`$env:GEMINI_API_KEY = Read-Host "Insira sua GEMINI_API_KEY"`).
- Garanta `EMBEDDINGS_PROVIDER=gemini` (no `.env` ou via variável de ambiente temporária).
- Execute novamente o indexador:

```pwsh
$env:EMBEDDINGS_PROVIDER = 'gemini'
python -m rag.indexer
Remove-Item Env:EMBEDDINGS_PROVIDER -ErrorAction SilentlyContinue
```

No Bash, utilize:

```bash
export GEMINI_API_KEY="sua_chave"
export EMBEDDINGS_PROVIDER=gemini
python -m rag.indexer
unset EMBEDDINGS_PROVIDER
```

## Execução do app

```pwsh
streamlit run project/app/streamlit_app.py
```

Por padrão o modelo de geração é `gemini-2.5-flash`. Edite `project/.env` para trocar modelo, top-K ou provedor de embeddings.

## Deploy no Streamlit Cloud

1. Publique este repositório no GitHub (privado ou público) e acesse [Streamlit Community Cloud](https://streamlit.io/cloud).
2. Clique em **New app**, selecione o repositório `the-go-getter11/rag-ipva-es`, branch `main` e informe `project/app/streamlit_app.py` no campo **Main file path**.
3. Em **Advanced settings**, garanta a versão do Python em `3.11` (ou compatível) e mantenha o `requirements.txt` raiz (já referencia `project/requirements.txt`).
4. Ainda nas configurações, abra **Secrets** e copie o conteúdo de `project/.streamlit/secrets.example.toml`, preenchendo pelo menos `GEMINI_API_KEY`. Ajuste valores adicionais se desejar (por exemplo `GENERATION_MODEL`, `TOP_K` ou habilitar busca via `GEMINI_ENABLE_GOOGLE_SEARCH`).
5. Salve as configurações e inicie o deploy. Na primeira execução o app gera automaticamente `project/data/index.pkl`; se a chave Gemini estiver ausente, ele cai em modo leitura com embeddings TF-IDF.

> Dica: para atualizar o deploy, basta fazer push na branch `main`. O Streamlit Cloud reconstruirá o app com as dependências e indexará novamente os documentos quando necessário.

## Qualidade de código

- **Lint (ruff)**
	```pwsh
	python -m ruff check project
	```
- **Testes (pytest)**
	```pwsh
	python -m pytest project/tests
	```

No Bash, utilize `python3` ou `ruff` diretamente conforme o ambiente.
