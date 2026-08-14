from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph


ROOT = Path(__file__).resolve().parents[1]
md_path = ROOT / "docs" / "melee-design-packet-v0.5.md"
docx_path = ROOT / "Atra_Melee_Design_Packet_v0.5.docx"


def normalize(text: str) -> str:
    text = text.replace("**", "").replace("`", "")
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^[-*]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\d+\.\s+", "", text, flags=re.MULTILINE)
    text = text.replace("|", " ")
    text = re.sub(r"\b:?-{3,}:?\b", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def iter_block_items(document: Document):
    for child in document.element.body.iterchildren():
        if child.tag.endswith("}p"):
            yield Paragraph(child, document)
        elif child.tag.endswith("}tbl"):
            yield Table(child, document)


md_lines = []
for line in md_path.read_text(encoding="utf-8").splitlines():
    if line.startswith("|") and all(
        re.fullmatch(r":?-{3,}:?", cell.strip())
        for cell in line.strip("|").split("|")
    ):
        continue
    md_lines.append(line)
md_text = normalize("\n".join(md_lines))

document = Document(docx_path)
doc_parts: list[str] = []
for item in iter_block_items(document):
    if isinstance(item, Paragraph):
        if item.text.strip():
            doc_parts.append(item.text)
    else:
        for row in item.rows:
            for cell in row.cells:
                doc_parts.append(cell.text)
doc_text = normalize("\n".join(doc_parts))

print(f"markdown_characters={len(md_text)}")
print(f"docx_characters={len(doc_text)}")
print(f"exact_normalized_match={md_text == doc_text}")
if md_text != doc_text:
    for index, (a, b) in enumerate(zip(md_text, doc_text)):
        if a != b:
            print(f"first_difference={index}")
            print(f"markdown_context={md_text[max(0,index-80):index+80]!r}")
            print(f"docx_context={doc_text[max(0,index-80):index+80]!r}")
            break
    raise SystemExit(1)
