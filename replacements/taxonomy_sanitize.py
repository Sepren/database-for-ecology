# Фильтрация «воды» и формулировок «метод не представлен» для method/product normalized.
import re

import pandas as pd

# Фрагменты, по которым строка не считается конкретной таксономией (RU/EN).
_VAGUE_PATTERNS = [
    r"не\s+представлен",
    r"не\s+указан[аоы]?\b",
    r"не\s+приводится",
    r"не\s+описан[аоы]?\b",
    r"не\s+раскрыва",
    r"не\s+сообща",
    r"отсутствует\s+в\s+контексте",
    r"отсутствует\s+в\s+тексте",
    r"в\s+контексте\s+не",
    r"нет\s+сведен",
    r"информация\s+отсутствует",
    r"недостаточно\s+данных",
    r"not\s+specified",
    r"not\s+available",
    r"not\s+presented",
    r"not\s+present\b",
    r"not\s+provided",
    r"no\s+information",
    r"лежащ(ий|ая|ие)\s+в\s+основе",
    r"в\s+основе\s+(данной|этой)\s+",
    r"метод(ом)?\s*,\s*лежащ",
    r"технологи(и|я)\s*,\s*котор",
    r"условно\s*[:-]",
    r"может\s+включать",
    r"в\s+том\s+числе\s+",
    r"и\s+т\.?\s*п\.?",
    r"и\s+друг(ие|их)\s+",
    r"различн(ые|ых)\s+(подход|метод)",
    r"см\.\s*выше",
    r"согласно\s+условиям",
    r"обобщённо",
    r"обобщенно",
]

_VAGUE_RE = re.compile(
    "|".join(f"(?:{p})" for p in _VAGUE_PATTERNS),
    re.IGNORECASE | re.UNICODE,
)


def is_vague_taxonomy_fragment(s: str) -> bool:
    if s is None:
        return True
    t = str(s).strip()
    if not t or t.lower() in ("nan", "none"):
        return True
    if t == "Прочее":
        return False
    if len(t) > 140:
        return True
    words = t.split()
    if len(words) > 14:
        return True
    if t.count(".") >= 2:
        return True
    if t.count("!") + t.count("?") >= 2:
        return True
    if _VAGUE_RE.search(t):
        return True
    return False


def sanitize_taxonomy_cell(value) -> str:
    """Убирает из списка через запятую «воду»; если ничего не осталось — «Прочее»."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "Прочее"
    s = str(value).strip()
    if not s or s.lower() in ("nan", "none"):
        return "Прочее"
    parts = [p.strip() for p in s.split(",") if p.strip()]
    good = [p for p in parts if not is_vague_taxonomy_fragment(p)]
    if not good:
        return "Прочее"
    out = []
    seen = set()
    for p in good:
        key = p.casefold()
        if key not in seen:
            seen.add(key)
            out.append(p)
    return ", ".join(out)


def clean_raw_fallback_label(val):
    """
    Разрешить подстановку из method_raw / product_raw только если это короткая конкретная метка,
    а не описательный абзац или «не представлен».
    """
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    s = " ".join(str(val).strip().split())
    if len(s) < 2:
        return None
    low = s.lower()
    if low in ("nan", "none", "-", "—", "нет", "n/a", "na"):
        return None
    if is_vague_taxonomy_fragment(s):
        return None
    if len(s) > 120:
        return None
    return s
