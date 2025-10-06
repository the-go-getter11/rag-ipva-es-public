"""Ferramentas de ingestão para documentos IPVA/ES."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, List, Optional

import yaml


PROJECT_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_DIR.parent


def _resolve_path(env_key: str, default: Path) -> Path:
    value = os.getenv(env_key)
    return Path(value) if value else default


DATASET_DOCS_DIR = _resolve_path("DATASET_DOCS_DIR", REPO_ROOT / "dataset/data/docs")
OUTPUT_DOCS_DIR = _resolve_path("OUTPUT_DOCS_DIR", PROJECT_DIR / "data/docs")
MANIFEST_PATH = _resolve_path("INGESTION_MANIFEST_PATH", PROJECT_DIR / "data/ingestion_manifest.json")


@dataclass
class DocumentMetadata:
    doc_id: str
    title: str
    uf: str
    source: str
    last_review: Optional[str]
    category: Optional[str]
    raw_path: str


def _normalise_first_line(line: str) -> dict:
    metadata = {}
    for chunk in filter(None, [part.strip() for part in line.split("|")]):
        if ":" not in chunk:
            continue
        key, value = chunk.split(":", 1)
        key = key.strip().lower().replace(" ", "_")
        metadata[key] = value.strip()
    return metadata


def _extract_last_review(lines: List[str]) -> tuple[Optional[str], List[str]]:
    pattern = re.compile(r"^Última revisão:\s*(\d{4}-\d{2}-\d{2})", re.IGNORECASE)
    filtered_lines: List[str] = []
    last_review: Optional[str] = None
    for line in lines:
        match = pattern.match(line.strip())
        if match and last_review is None:
            last_review = match.group(1)
            continue
        filtered_lines.append(line)
    return last_review, filtered_lines


def _extract_first_heading(lines: List[str]) -> tuple[Optional[str], List[str]]:
    heading_pattern = re.compile(r"^#\s+(.*)")
    category: Optional[str] = None
    for line in lines:
        match = heading_pattern.match(line.strip())
        if match:
            category = match.group(1).strip()
            break
    return category, lines


def _slugify(path: Path) -> str:
    return "/".join(path.with_suffix("").parts[-2:]) if len(path.parts) >= 2 else path.stem


def convert_markdown(path: Path) -> tuple[DocumentMetadata, str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines:
        raise ValueError(f"Documento vazio: {path}")

    header_meta = _normalise_first_line(lines[0])
    body_lines = lines[1:]

    last_review, body_lines = _extract_last_review(body_lines)
    category, body_lines = _extract_first_heading(body_lines)
    content = "\n".join(body_lines).strip() + "\n"

    doc_id = _slugify(path.relative_to(DATASET_DOCS_DIR))
    metadata = DocumentMetadata(
        doc_id=doc_id,
        title=category or path.stem.replace("_", " ").title(),
        uf=header_meta.get("uf", "ES"),
        source=header_meta.get("fonte", ""),
        last_review=last_review,
        category=category,
        raw_path=path.relative_to(DATASET_DOCS_DIR).as_posix(),
    )

    front_matter = "---\n" + yaml.safe_dump({k: v for k, v in asdict(metadata).items() if v}, sort_keys=False, allow_unicode=True) + "---\n\n"
    return metadata, front_matter + content


def _iter_markdown_files(root: Path) -> Iterable[Path]:
    for file in sorted(root.rglob("*.md")):
        if file.is_file():
            yield file


def ingest_documents(dataset_dir: Path = DATASET_DOCS_DIR, output_dir: Path = OUTPUT_DOCS_DIR) -> list[DocumentMetadata]:
    if not dataset_dir.exists():
        raise FileNotFoundError(f"Diretório de origem não encontrado: {dataset_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    collected: List[DocumentMetadata] = []
    for md_path in _iter_markdown_files(dataset_dir):
        metadata, content = convert_markdown(md_path)
        output_path = output_dir / f"{metadata.doc_id.replace('/', '__')}.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        collected.append(metadata)

    collected.sort(key=lambda item: item.doc_id)
    MANIFEST_PATH.write_text(json.dumps([asdict(m) for m in collected], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return collected


if __name__ == "__main__":
    created = ingest_documents()
    print(f"[OK] Ingeridos {len(created)} documentos para {OUTPUT_DOCS_DIR}")
