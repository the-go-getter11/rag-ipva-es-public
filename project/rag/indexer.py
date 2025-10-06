import os, pickle, pathlib
from typing import Tuple, Dict, Any

import yaml
from .utils import Chunk
from .embeddings import GeminiEmbedder, TfidfEmbedder
from dotenv import load_dotenv
load_dotenv()
PROJECT_DIR=pathlib.Path(__file__).resolve().parents[1]
DATA_DIR=PROJECT_DIR/'data'; DOCS_DIR=DATA_DIR/'docs'; INDEX=DATA_DIR/'index.pkl'


def _split_front_matter(text: str) -> Tuple[Dict[str, Any], str]:
  if text.lstrip().startswith('---'):
    parts=text.split('---',2)
    if len(parts)>=3:
      _,front,body=parts
      meta=yaml.safe_load(front) or {}
      return meta, body.lstrip()
  return {}, text


def load_docs():
  chunks=[]
  if not DOCS_DIR.exists():
    return chunks
  for p in DOCS_DIR.glob('*.md'):
    raw=p.read_text(encoding='utf-8')
    meta,body=_split_front_matter(raw)
    doc_id=meta.get('doc_id',p.stem)
    chunks.append(Chunk(
      doc_id=doc_id,
      title=meta.get('title', p.stem),
      uf=meta.get('uf','ES'),
      source_url=meta.get('source_url',''),
      text=body,
      source=meta.get('source',''),
      last_review=meta.get('last_review'),
      category=meta.get('category'),
      metadata=meta
    ))
  return chunks

def build_index():
  prov=os.getenv('EMBEDDINGS_PROVIDER','gemini').lower(); cs=load_docs()
  payload={'provider':prov, 'chunks': cs}
  if not cs:
    payload={'provider':prov, 'chunks': [], 'vectors': []}
    INDEX.parent.mkdir(parents=True,exist_ok=True); pickle.dump(payload, open(INDEX,'wb'))
    print('[WARN] Nenhum documento encontrado; índice vazio gerado em', INDEX)
    return payload

  tx=[c.text for c in cs]
  provider_used=prov
  vectorizer=None
  vectors=None
  if prov=='gemini':
    try:
      embedder=GeminiEmbedder(); vectors=embedder.embed(tx)
    except Exception as exc:
      print('[WARN] Falha ao usar embeddings Gemini:', exc, '— alternando para TF-IDF.')
      provider_used='tfidf'; embedder=TfidfEmbedder(); vectors=embedder.embed(tx); vectorizer=embedder.v
    else:
      payload['vectors']=vectors
  if provider_used!='gemini':
    if provider_used!='tfidf':
      provider_used='tfidf'
    if vectors is None:
      embedder=TfidfEmbedder(); vectors=embedder.embed(tx); vectorizer=embedder.v
    payload['vectors']=vectors
    if vectorizer is None:
      vectorizer=getattr(embedder,'v',None)
  payload['provider']=provider_used
  if vectorizer is not None:
    payload['vectorizer']=vectorizer
  INDEX.parent.mkdir(parents=True,exist_ok=True); pickle.dump(payload, open(INDEX,'wb'))
  print('[OK] index', INDEX)
  return payload
if __name__=='__main__': build_index()
