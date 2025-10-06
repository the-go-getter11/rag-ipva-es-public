import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if PROJECT_ROOT not in [Path(p) for p in sys.path]:
  sys.path.insert(0, str(PROJECT_ROOT))

INDEX_PATH = PROJECT_ROOT / "data" / "index.pkl"

import streamlit as st
import importlib
import json
import time


def ensure_index():
  if INDEX_PATH.exists():
    return
  try:
    with st.spinner("Gerando índice inicial…"):
      import rag.indexer as indexer_module
      indexer_module.build_index()
  except Exception as exc:  # pragma: no cover - feedback para usuário final
    st.error(
      "Não foi possível gerar o índice automaticamente. "
      "Verifique as credenciais e tente novamente."
    )
    raise exc


def load_engine():
  ensure_index()
  try:
    import rag.engine as engine_module
  except ModuleNotFoundError as exc:  # pragma: no cover - defensive guard for misconfigured path
    st.error(
      "Não foi possível carregar o módulo 'rag'. Verifique se o diretório do projeto está no PYTHONPATH."
    )
    raise exc
  # Evita reload explícito para não quebrar imports relativos em ambientes como Streamlit Cloud
  return engine_module.Engine()


def render_sources(result):
  cites = result.get('citations', [])
  if cites:
    st.markdown("### Fontes")
    for i, c in enumerate(cites, start=1):
      url = c.get('url') or ''
      title = c.get('title') or c.get('id')
      meta = []
      if c.get('id'):
        meta.append(c['id'])
      if c.get('category'):
        meta.append(c['category'])
      meta_str = f" — {' | '.join(meta)}" if meta else ''
      if url:
        st.markdown(f"[{i}] [{title}]({url}){meta_str}")
      else:
        st.markdown(f"[{i}] {title}{meta_str}")

      excerpt = c.get('excerpt')
      if excerpt:
        with st.expander(f"Ver trecho [{i}]"):
          st.write(excerpt)

  web_cites = result.get('web_citations', [])
  if web_cites:
    st.markdown("### Fontes (web)")
    for i, c in enumerate(web_cites, start=1):
      url = c.get('url') or ''
      title = c.get('title') or url or 'Fonte web'
      if url:
        st.markdown(f"- [{title}]({url})")
      else:
        st.markdown(f"- {title}")


st.set_page_config(page_title="RAG IPVA — ES")
st.title("RAG IPVA — ES")
st.caption("Modelo padrão: gemini-2.5-flash (edite .env para trocar).")

# Recria o Engine em cada execução para garantir que mudanças de código sejam aplicadas
st.session_state.engine = load_engine()

tab_pergunta, tab_links = st.tabs(["Pergunta", "Links úteis"])

with tab_pergunta:
  question = st.text_input("Pergunta:")
  if st.button("Consultar") and question.strip():
    start = time.perf_counter()
    placeholder = st.empty()
    streamed_text = ""
    result_meta = None
    with st.spinner("Consultando o modelo..."):
      for event in st.session_state.engine.stream_answer(question):
        if event.get('type') == 'text':
          streamed_text += event.get('content', '')
          placeholder.markdown(streamed_text)
        elif event.get('type') == 'metadata':
          result_meta = event.get('content')
    if result_meta and not streamed_text:
      placeholder.markdown(result_meta.get('text', ''))
    elapsed = time.perf_counter() - start

    # Exibe tempo decorrido
    st.caption(f"Tempo de resposta: {elapsed:.2f}s")

    if result_meta:
      render_sources(result_meta)
    elif streamed_text:
      st.write(streamed_text)

with tab_links:
  st.markdown("### Portais e páginas úteis (SEFAZ/ES)")
  default_links = [
    {"titulo": "IPVA - Página principal (SEFAZ)", "url": "https://internet.sefaz.es.gov.br/agenciavirtual/area_publica/ipva/index.php"},
    {"titulo": "Informações IPVA (SEFAZ)", "url": "https://sefaz.es.gov.br/informacoes-ipva"},
    {"titulo": "Legislação IPVA (SEFAZ)", "url": "https://internet.sefaz.es.gov.br/agenciavirtual/area_publica/ipva/legislacao.php"},
    {"titulo": "Fale Conosco (Receita Estadual)", "url": "https://s1-internet.sefaz.es.gov.br/faleconosco"},
    {"titulo": "SIC - Serviço de Informação ao Cidadão (SEFAZ)", "url": "https://sefaz.es.gov.br/servico-de-informacao-ao-cidadao-sic"},
  ]

  # Inclui fontes do dataset, se disponíveis
  sources_path = PROJECT_ROOT.parent / 'dataset' / 'data' / 'sources' / 'sources_es.json'
  refs = []
  try:
    if sources_path.exists():
      data = json.loads(sources_path.read_text(encoding='utf-8'))
      refs = data.get('refs', [])
  except Exception:
    pass

  all_links = default_links + refs
  for item in all_links:
    t = item.get('titulo') or item.get('title') or 'Link'
    u = item.get('url') or ''
    st.markdown(f"- [{t}]({u})")
