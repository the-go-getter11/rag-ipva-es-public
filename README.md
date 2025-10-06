# RAG-IPVA — ES (Public)

Assistente tributário para IPVA do Espírito Santo com RAG, Gemini, TF-IDF e interface Streamlit.

## Deploy no Streamlit Cloud

1. Crie um app em [Streamlit Cloud](https://streamlit.io/cloud) usando este repositório público.
2. Configure o arquivo principal como `project/app/streamlit_app.py`.
3. Em "Secrets", adicione:
   - `GEMINI_API_KEY = "SUA_CHAVE_GEMINI"`
   - `GENERATION_MODEL = "gemini-2.5-flash"`
   - `EMBEDDINGS_PROVIDER = "gemini"`
   - `TOP_K = 4`
   - `GEMINI_ENABLE_GOOGLE_SEARCH = true`
   - `DATASET_DOCS_DIR = "dataset/data/docs"`
   - `OUTPUT_DOCS_DIR = "project/data/docs"`
   - `INGESTION_MANIFEST_PATH = "project/data/ingestion_manifest.json"`
4. O app irá gerar o índice automaticamente na primeira execução.

## Estrutura
- `project/app/streamlit_app.py`: Interface principal
- `project/rag/engine.py`, `indexer.py`, `embeddings.py`, `ingestion.py`, `utils.py`: Núcleo RAG
- `dataset/data/docs/`: Documentos normativos IPVA/ES
- `project/data/`: Dados processados e índice
- `project/tests/`: Testes automatizados
- `guides/`: Documentação técnica e prompts

## Licença
Este repositório é público para deploy e demonstração. Remova ou substitua dados sensíveis antes de publicar em produção.
