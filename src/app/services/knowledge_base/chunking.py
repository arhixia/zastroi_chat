_CHARS_PER_TOKEN = 3


def count_tokens(text: str) -> int:
    return max(1, len(text) // _CHARS_PER_TOKEN)


def split_into_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Режет текст на чанки примерно по chunk_size токенов с overlap токенов
    пересечения между соседними чанками (чтобы не терять смысл на границе).
    """
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    if not paragraphs:
        return []

    chunks: list[str] = []
    current: list[str] = []
    current_tokens = 0

    def flush():
        if current:
            chunks.append("\n".join(current))

    for para in paragraphs:
        para_tokens = count_tokens(para)

        if para_tokens > chunk_size:
            flush()
            current.clear()
            current_tokens = 0

            chars_per_chunk = chunk_size * _CHARS_PER_TOKEN
            overlap_chars = overlap * _CHARS_PER_TOKEN
            step = max(chars_per_chunk - overlap_chars, 1)
            for i in range(0, len(para), step):
                chunks.append(para[i : i + chars_per_chunk])
            continue

        if current_tokens + para_tokens > chunk_size:
            flush()
            # переносим хвост предыдущего чанка в новый для overlap
            overlap_paras: list[str] = []
            overlap_tokens = 0
            for p in reversed(current):
                t = count_tokens(p)
                if overlap_tokens + t > overlap:
                    break
                overlap_paras.insert(0, p)
                overlap_tokens += t
            current = overlap_paras
            current_tokens = overlap_tokens

        current.append(para)
        current_tokens += para_tokens

    flush()
    return chunks