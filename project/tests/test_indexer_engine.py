from pathlib import Path
import os

from rag import indexer
from rag.engine import Engine


def test_build_index_and_engine(tmp_path: Path, monkeypatch):
    # Redirect data dir to temp
    data_dir = tmp_path / "data"
    docs_dir = data_dir / "docs"
    docs_dir.mkdir(parents=True)
    index_file = data_dir / "index.pkl"

    # Create minimal doc with front matter
    md = (
        "---\n"
        "doc_id: test/doc\n"
        "title: Teste Doc\n"
        "uf: ES\n"
        "source_url: http://example.com\n"
        "---\n\n"
        "Conteúdo de teste para indexação."
    )
    (docs_dir / "doc.md").write_text(md, encoding="utf-8")

    # Patch module paths
    monkeypatch.setattr(indexer, "DATA_DIR", data_dir)
    monkeypatch.setattr(indexer, "DOCS_DIR", docs_dir)
    monkeypatch.setattr(indexer, "INDEX", index_file)

    payload = indexer.build_index()
    assert (index_file).exists()
    assert payload["vectors"]

    # Point Engine to our temp index
    from rag import engine as engine_mod
    engine_mod.INDEX = str(index_file)
    eng = Engine()
    out = list(eng.stream_answer("O que diz o documento?"))
    assert out


def test_engine_offline_mode(monkeypatch):
    from rag import engine as engine_mod
    monkeypatch.setenv("GEMINI_API_KEY", "")
    eng = Engine()
    events = list(eng.stream_answer("Pergunta"))
    assert any(e.get("type") == "text" for e in events)


def test_indexer_fallback_tfidf(monkeypatch, tmp_path):
    from rag import indexer as idx

    # Prepare a docs dir
    docs = tmp_path / "docs"
    data_dir = tmp_path
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "x.md").write_text(
        "---\n"
        "doc_id: x\n"
        "title: X\n"
        "---\n\n"
        "Teste TF-IDF.\n",
        encoding="utf-8",
    )

    # Force provider to gemini, but remove key so it fails and falls back
    monkeypatch.setenv("EMBEDDINGS_PROVIDER", "gemini")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    idx.DOCS_DIR = docs
    idx.DATA_DIR = data_dir
    idx.INDEX = data_dir / "index.pkl"
    payload = idx.build_index()
    assert payload["provider"] == "tfidf"
