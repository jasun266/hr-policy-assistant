"""Policy search. Each `## section` of a markdown policy is one chunk, ranked with BM25.

ponytail: keyword search is enough for a handful of documents; switch to embeddings plus
a vector store (e.g. pgvector) when the policy library grows or questions get paraphrased."""

import re
from pathlib import Path

from rank_bm25 import BM25Okapi

POLICY_DIR = Path(__file__).resolve().parent.parent / "policies"
_TOKEN = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return _TOKEN.findall(text.lower())


class PolicyIndex:
    def __init__(self, directory: Path = POLICY_DIR):
        self.chunks: list[dict] = []
        for path in sorted(directory.glob("*.md")):
            title, section, lines = path.stem, None, []
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.startswith("# "):
                    title = line[2:].strip()
                elif line.startswith("## "):
                    self._add(title, section, lines)
                    section, lines = line[3:].strip(), []
                else:
                    lines.append(line)
            self._add(title, section, lines)
        self._bm25 = BM25Okapi([tokenize(f"{c['document']} {c['section']} {c['text']}") for c in self.chunks])

    def _add(self, document: str, section: str | None, lines: list[str]) -> None:
        text = "\n".join(lines).strip()
        if section and text:
            self.chunks.append({"document": document, "section": section, "text": text})

    def search(self, query: str, k: int = 3) -> list[dict]:
        scores = self._bm25.get_scores(tokenize(query))
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        return [{**self.chunks[i], "score": round(float(scores[i]), 3)} for i in ranked[:k] if scores[i] > 0]
