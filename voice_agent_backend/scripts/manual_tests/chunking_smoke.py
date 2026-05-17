import sys
import os
from pathlib import Path

# Mock settings
class MockSettings:
    CHUNK_SIZE = 1200
    CHUNK_OVERLAP = 200

settings = MockSettings()

# Re-implementing parts of ingest.py for testing
import re
def chunk_text_simple(text: str) -> list[str]:
    separators = ["\n\n", "\n", ". ", ", ", " "]
    def recursive_split_inner(txt: str, max_len: int, seps: list) -> list[str]:
        if len(txt) <= max_len: return [txt]
        if not seps: return [txt[i : i + max_len] for i in range(0, len(txt), max_len)]
        sep = seps[0]
        rest = seps[1:]
        pieces = txt.split(sep)
        if len(pieces) <= 1: return recursive_split_inner(txt, max_len, rest)
        result = []
        for piece in pieces:
            if len(piece) <= max_len: result.append(piece)
            else: result.extend(recursive_split_inner(piece, max_len, rest))
        return result

    raw_pieces = recursive_split_inner(text, settings.CHUNK_SIZE, separators)
    merged = []
    current = ""
    for piece in raw_pieces:
        t = piece.strip()
        if not t: continue
        if len(current) + len(t) + 1 <= settings.CHUNK_SIZE:
            current += (" " if current else "") + t
        else:
            if current: merged.append(current)
            current = t
    if current: merged.append(current)
    overlapped = []
    for j, chunk in enumerate(merged):
        if j == 0: overlapped.append(chunk)
        else:
            tail = merged[j - 1][-settings.CHUNK_OVERLAP:]
            last_sent_end = tail.rfind(". ")
            if last_sent_end > 0: tail = tail[last_sent_end + 2 :]
            overlapped.append("..." + tail + " " + chunk)
    return overlapped

# text from the user image
sample_text = """Q: Do you have physical retail stores?

A: Yes, we have flagship stores in New York (SoHo), Los Angeles (Beverly Hills), London (Mayfair), Paris (Le Marais), and Tokyo (Shibuya). Additionally, our dresses are available in over 200 select department stores and boutiques worldwide, including Nordstrom, Bloomingdale's, and Harrods. You can use our store locator tool on our website to find the nearest retail location. Our flagship stores offer personal styling services by appointment.
"""

lines = sample_text.split("\n")
# Assuming chunk_structured_lines logic
current_block = sample_text
chunks = chunk_text_simple(current_block)

print(f"Total chunks: {len(chunks)}")
for i, c in enumerate(chunks):
    print(f"\n--- Chunk {i} ---")
    print(c)
    print(f"Length: {len(c)}")
