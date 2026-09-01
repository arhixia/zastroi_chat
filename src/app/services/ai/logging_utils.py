import logging
import sys

logger = logging.getLogger("ai")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s [AI] %(message)s", "%H:%M:%S"))
    logger.addHandler(handler)
    logger.propagate = False


def _preview_messages(messages: list[dict], limit: int = 300) -> str:
    return " | ".join(f"{m['role']}: {m['content'][:limit]}" for m in messages)


def _format_cost(usage) -> str:
    cost = getattr(usage, "cost", None)
    return f"${cost:.6f}" if cost is not None else "н/д"


def log_chat_call(label: str, messages: list[dict], response) -> None:
    usage = getattr(response, "usage", None)
    answer = response.choices[0].message.content or ""

    logger.info("[%s] запрос: %s", label, _preview_messages(messages))
    logger.info("[%s] ответ: %s", label, answer[:300])

    if usage:
        logger.info(
            "[%s] токены: prompt=%s completion=%s total=%s стоимость=%s",
            label, usage.prompt_tokens, usage.completion_tokens, usage.total_tokens,
            _format_cost(usage),
        )


def log_embedding_call(label: str, n_texts: int, response) -> None:
    usage = getattr(response, "usage", None)
    logger.info(
        "[%s] эмбеддинги: текстов=%s токены=%s стоимость=%s",
        label, n_texts,
        usage.total_tokens if usage else "н/д",
        _format_cost(usage) if usage else "н/д",
    )