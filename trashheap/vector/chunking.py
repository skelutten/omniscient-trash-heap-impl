"""Multi-chunk passage splitting and frontmatter stripping (Plan 90 Phase V2, D81)."""

import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ChunkRecord:
    """Passage chunk representation of a Knowledge Object section."""

    chunk_index: int
    text: str
    word_count: int
    header: Optional[str] = None


def strip_frontmatter(content: str) -> str:
    """Strip YAML frontmatter from Markdown content (RETRIEVAL.md §9.1 item 4).

    Frontmatter metadata is queried deterministically via Step 2 pre-filters;
    embedding raw YAML would corrupt semantic similarity with schema keywords.
    """
    parts = content.split("---", 2)
    if len(parts) >= 3:
        # Return content after the second '---' fence
        return parts[2].strip()
    return content.strip()


def chunk_markdown(
    raw_markdown: str,
    target_words: int = 256,
    max_words: int = 512,
) -> List[ChunkRecord]:
    """Split Markdown body into multi-chunk passages adhering to section boundaries."""
    body = strip_frontmatter(raw_markdown)
    if not body:
        return [ChunkRecord(chunk_index=0, text="", word_count=0)]

    # Split by markdown headers (e.g. ## Section)
    header_pattern = re.compile(r"^(#{1,6}\s+.*)$", re.MULTILINE)
    sections = header_pattern.split(body)

    chunks: List[ChunkRecord] = []
    current_header: Optional[str] = None
    chunk_idx = 0

    i = 0
    while i < len(sections):
        part = sections[i].strip()
        if not part:
            i += 1
            continue

        if header_pattern.match(part):
            current_header = part
            i += 1
            content_part = sections[i].strip() if i < len(sections) else ""
            i += 1
        else:
            content_part = part
            i += 1

        words = content_part.split()
        if not words and current_header:
            chunks.append(
                ChunkRecord(
                    chunk_index=chunk_idx,
                    text=current_header,
                    word_count=len(current_header.split()),
                    header=current_header,
                )
            )
            chunk_idx += 1
            continue

        # If content within target bounds, emit as single chunk
        if len(words) <= max_words:
            full_text = f"{current_header}\n\n{content_part}" if current_header else content_part
            chunks.append(
                ChunkRecord(
                    chunk_index=chunk_idx,
                    text=full_text,
                    word_count=len(full_text.split()),
                    header=current_header,
                )
            )
            chunk_idx += 1
        else:
            # Paragraph-based subdivision for long sections
            paragraphs = content_part.split("\n\n")
            curr_para_words: List[str] = []
            for p in paragraphs:
                p_words = p.split()
                if len(curr_para_words) + len(p_words) > max_words and curr_para_words:
                    sub_text = " ".join(curr_para_words)
                    full_text = f"{current_header}\n\n{sub_text}" if current_header else sub_text
                    chunks.append(
                        ChunkRecord(
                            chunk_index=chunk_idx,
                            text=full_text,
                            word_count=len(full_text.split()),
                            header=current_header,
                        )
                    )
                    chunk_idx += 1
                    curr_para_words = list(p_words)
                else:
                    curr_para_words.extend(p_words)

            if curr_para_words:
                sub_text = " ".join(curr_para_words)
                full_text = f"{current_header}\n\n{sub_text}" if current_header else sub_text
                chunks.append(
                    ChunkRecord(
                        chunk_index=chunk_idx,
                        text=full_text,
                        word_count=len(full_text.split()),
                        header=current_header,
                    )
                )
                chunk_idx += 1

    if not chunks:
        chunks.append(ChunkRecord(chunk_index=0, text=body, word_count=len(body.split())))

    return chunks
