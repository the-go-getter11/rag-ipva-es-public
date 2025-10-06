from google import genai
from sklearn.feature_extraction.text import TfidfVectorizer
import os, numpy as np
class GeminiEmbedder:
  def __init__(self, model='text-embedding-004'):
    k=os.getenv('GEMINI_API_KEY','')
    if not k: raise RuntimeError('GEMINI_API_KEY não definido.')
    self.client=genai.Client(api_key=k); self.model=model
  def embed(self, texts):
    embeddings=[]
    # Prefer API that supports batching; fallback to per-item requests.
    batch_method=getattr(self.client.models,'batch_embed_contents',None)
    if batch_method:
      r=batch_method(model=self.model, requests=[{'content':t} for t in texts])
      embeddings=[np.array(e.values,dtype='float32') for e in r.embeddings]
    else:
      for t in texts:
        resp=self.client.models.embed_content(model=self.model, contents=[{'text':t}])
        emb=getattr(resp,'embedding',None)
        if emb is None:
          emb = resp.embeddings[0]
        embeddings.append(np.array(emb.values,dtype='float32'))
    return np.vstack(embeddings)
class TfidfEmbedder:
  def __init__(self):
    self.v=TfidfVectorizer(strip_accents='unicode',lowercase=True,ngram_range=(1,2),max_features=50000)
    self.f=False
  def fit(self, texts): self.v.fit(texts); self.f=True
  def embed(self,texts):
    if not self.f: self.fit(texts)
    return self.v.transform(texts).toarray().astype('float32')
