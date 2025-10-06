from pathlib import Path
from rag import ingestion


def test_convert_markdown_roundtrip(tmp_path: Path):
    raw = tmp_path / "ES_real__00_base_legal.md"
    raw.write_text(
        "UF: ES | Fonte: Lei 6.999/2001; RIPVA\n\n# Base legal\nÚltima revisão: 2025-10-05\n\nTexto...\n",
        encoding="utf-8",
    )

    md, output = ingestion.convert_markdown(raw)
    assert md.doc_id.endswith("ES_real__00_base_legal")
    assert "---\n" in output and "\n---\n\n" in output


def test_ingest_documents(tmp_path: Path, monkeypatch):
    src = tmp_path / "dataset_docs"
    src.mkdir(parents=True)
    (src / "a.md").write_text("UF: ES | Fonte: X\n\n# Título\n\nCorpo.", encoding="utf-8")

    out = tmp_path / "out_docs"

    monkeypatch.setenv("DATASET_DOCS_DIR", str(src))
    monkeypatch.setenv("OUTPUT_DOCS_DIR", str(out))
    monkeypatch.setenv("INGESTION_MANIFEST_PATH", str(tmp_path / "manifest.json"))

    created = ingestion.ingest_documents()
    assert created and any(d.title for d in created)
