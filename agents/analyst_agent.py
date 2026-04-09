import pandas as pd
from .base_agent import BaseAgent
from replacements.tech_replacements import METHOD_PATTERNS, PRODUCT_PATTERNS, extract_all_tags
from replacements.taxonomy_sanitize import (
    clean_raw_fallback_label,
    sanitize_taxonomy_cell,
)


class AnalystAgent(BaseAgent):
    def __init__(self):
        super().__init__("AnalystAgent")

    def execute(self, df):
        self.log("💡 Глубокий анализ: Сканирование всех текстовых полей...")

        # Собираем данные из всех возможных источников в статье
        search_fields = [
            "title",
            "abstract",
            "method_raw",
            "technology_raw",
            "concept",
            "findings",
            "conclusion",
            "results",
            "content",
            "terms",
        ]
        valid_fields = [f for f in search_fields if f in df.columns]

        # Создаем единое текстовое поле для анализа каждой строки
        full_context = df[valid_fields].fillna("").agg(" ".join, axis=1)

        # Извлекаем ВСЕ методы и продукты
        df["method_normalized"] = full_context.apply(lambda x: extract_all_tags(x, METHOD_PATTERNS))
        df["product_normalized"] = full_context.apply(lambda x: extract_all_tags(x, PRODUCT_PATTERNS))

        if "method_raw" in df.columns:
            raw_fb = df["method_raw"].apply(clean_raw_fallback_label)
            take = (df["method_normalized"] == "Прочее") & raw_fb.notna()
            df.loc[take, "method_normalized"] = raw_fb.loc[take]

        if "product_raw" in df.columns:
            raw_p = df["product_raw"].apply(clean_raw_fallback_label)
            take_p = (df["product_normalized"] == "Прочее") & raw_p.notna()
            df.loc[take_p, "product_normalized"] = raw_p.loc[take_p]

        df["method_normalized"] = df["method_normalized"].apply(sanitize_taxonomy_cell)
        df["product_normalized"] = df["product_normalized"].apply(sanitize_taxonomy_cell)

        return df, {"count": len(df)}