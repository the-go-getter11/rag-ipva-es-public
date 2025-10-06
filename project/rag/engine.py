import os,pickle,numpy as np
from pathlib import Path
from google import genai
from .utils import Chunk
from dotenv import load_dotenv
load_dotenv()
PROJECT_DIR=Path(__file__).resolve().parents[1]
INDEX=str(PROJECT_DIR/'data'/'index.pkl')


def _get_secrets():
  try:
    import streamlit as st  # noqa: WPS433 (runtime import)
    return getattr(st, 'secrets', None)
  except Exception:
    return None


def _get_conf(key, default=None, cast=str):
  val=None
  secrets=_get_secrets()
  # Prefer Streamlit secrets when available
  if secrets is not None:
    try:
      if key in secrets:
        val=secrets[key]
    except Exception:
      try:
        val=secrets.get(key, None)  # type: ignore[attr-defined]
      except Exception:
        pass
  if val is None:
    val=os.getenv(key, None)
  if val is None:
    return default
  # Casting
  if cast is bool:
    if isinstance(val, bool):
      return val
    return str(val).strip().lower() in ('1','true','yes','on')
  if cast is int:
    try:
      return int(val)
    except Exception:
      return default
  if cast is float:
    try:
      return float(val)
    except Exception:
      return default
  return val
def cos(a,b):
  d=(np.linalg.norm(a)*np.linalg.norm(b)) or 1e-9
  return float(np.dot(a,b)/d)
class Engine:
  def __init__(s):
    s.idx=pickle.load(open(INDEX,'rb'))
    s.prov=s.idx['provider']; s.vecs=s.idx['vectors']; s.chunks=s.idx['chunks']
    s.vectorizer=s.idx.get('vectorizer')
    s.top=_get_conf('TOP_K', 4, cast=int)
    s.key=_get_conf('GEMINI_API_KEY', '')
    s.model=_get_conf('GENERATION_MODEL','gemini-2.5-flash')
    s.cli=genai.Client(api_key=s.key) if s.key else None
  def retrieve(s,q):
    from .embeddings import GeminiEmbedder,TfidfEmbedder
    if s.prov=='gemini':
      E=GeminiEmbedder(); qv=E.embed([q])[0]
    else:
      if s.vectorizer is None:
        E=TfidfEmbedder(); qv=E.embed([q])[0]
      else:
        qv=s.vectorizer.transform([q]).toarray().astype('float32')[0]
    sims=[(cos(qv,v),i) for i,v in enumerate(s.vecs)]
    sims.sort(reverse=True); idx=[j for _,j in sims[:s.top]]; return [s.chunks[j] for j in idx]
  def _format_citations(s,chunks):
    return [
      {
        'id': c.doc_id,
        'title': c.title,
        'url': c.source_url or c.metadata.get('source_url','') or '',
        'source': c.source,
        'category': c.category,
        'excerpt': (c.text[:400] + ('…' if len(c.text) > 400 else '')),
      } for c in chunks
    ]
  def _extract_web_refs(s,resp):
    refs=[]
    if not resp: return refs
    for attr in ('citations','grounding_metadata','groundingMetadata'):
      md = getattr(resp, attr, None)
      if not md:
        continue
      items=[]
      try:
        if isinstance(md,(list,tuple)):
          items=md
        elif isinstance(md,dict):
          for k in ('supportingDocs','sources','web_results','webResults','attributions'):
            if k in md and isinstance(md[k],(list,tuple)):
              items=md[k]; break
      except Exception:
        pass
      for it in items:
        try:
          url = it.get('uri') or it.get('url') or ''
          title = it.get('title') or it.get('titleText') or ''
          if url or title:
            refs.append({'title': title, 'url': url})
        except Exception:
          continue
    return refs
  def _build_response(s,text,chunks,resp):
    return {
      'text': text,
      'citations': s._format_citations(chunks),
      'web_citations': s._extract_web_refs(resp)
    }
  def _build_request(s,q):
    chunks=s.retrieve(q)
    ctx='\n\n'.join([f'[{i+1}] {c.title} — {c.doc_id}\n{c.text}' for i,c in enumerate(chunks)])
    sys='Você é especialista em IPVA/ES. Responda em pt-BR, cite [n] e datas/vigências.'
    enable_search = _get_conf('GEMINI_ENABLE_GOOGLE_SEARCH', False, cast=bool)
    user = f'Pergunta: {q}\n\nContexto:\n{ctx}' if chunks else q
    cfg={'system_instruction': sys}
    if enable_search:
      cfg['tools']=[{'google_search':{}}]
    contents=[{'role':'user','parts':[{'text':user}]}]
    return chunks, contents, cfg
  def answer(s,q):
    chunks, contents, cfg = s._build_request(q)
    if not s.cli:
      return s._build_response('[Modo leitura] defina GEMINI_API_KEY.', chunks, None)
    r=s.cli.models.generate_content(model=s.model, contents=contents, config=cfg)
    text=getattr(r,'text',None) or ''
    return s._build_response(text, chunks, r)
  def stream_answer(s,q):
    chunks, contents, cfg = s._build_request(q)
    if not s.cli:
      offline='[Modo leitura] defina GEMINI_API_KEY.'
      yield {'type':'text','content': offline}
      yield {'type':'metadata','content': s._build_response(offline, chunks, None)}
      return
    stream_method=getattr(s.cli.models,'generate_content_stream',None)
    responses=None
    if callable(stream_method):
      responses=stream_method(model=s.model, contents=contents, config=cfg)
    else:
      try:
        responses=s.cli.models.generate_content(model=s.model, contents=contents, config=cfg, stream=True)
      except TypeError:
        single=s.cli.models.generate_content(model=s.model, contents=contents, config=cfg)
        text=getattr(single,'text',None) or ''
        if text:
          yield {'type':'text','content':text}
        yield {'type':'metadata','content': s._build_response(text, chunks, single)}
        return
    collected=[]; final_event=None
    for event in responses:
      final_event=event
      text=getattr(event,'text',None)
      if text:
        collected.append(text)
        yield {'type':'text','content':text}
    final_text=''.join(collected)
    yield {'type':'metadata','content': s._build_response(final_text, chunks, final_event)}
