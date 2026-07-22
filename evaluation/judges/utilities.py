import re


class Utilities:
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize text for deterministic keyword matching.
        """
        text = text.lower()

        # Treat hyphens/underscores as spaces.
        text = text.replace("-", " ")
        text = text.replace("_", " ")

        # Remove punctuation.
        text = re.sub(r"[^\w\s]", "", text)

        # Collapse repeated whitespace.
        text = re.sub(r"\s+", " ", text).strip()

        return text