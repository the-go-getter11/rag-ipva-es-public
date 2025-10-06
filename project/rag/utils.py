from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class Chunk:
    doc_id: str
    title: str
    uf: str
    source_url: str
    text: str
    source: str = ""
    last_review: Optional[str] = None
    category: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
