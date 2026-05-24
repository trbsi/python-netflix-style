import re

import spacy
from django.core import signing
from django.db.models import QuerySet
from spacy.cli import download

from src.discovery.models import TagAlias
from src.events.events import enqueue_search_event


class PersonalizeSiteService():
    def personalize_site(self, text: str, session_id: str | None) -> str | None:
        enqueue_search_event(session_id, text)

        text = self.clean_query(text)
        text_array = self.to_tokens(text)
        canonical_tags = self.get_canonical_tags(text_array)
        extra_tags = [tag for tag in text_array if tag not in canonical_tags]

        signed_value = signing.dumps({
            "query": text,
            "canonical_tags": canonical_tags,
            "extra_tags": extra_tags,
        })

        return signed_value

    def clean_query(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def to_tokens(self, text: str) -> list:
        model_name = 'en_core_web_sm'
        try:
            nlp = spacy.load(model_name)
        except OSError:
            download(model_name)
            nlp = spacy.load(model_name)

        doc = nlp(text)

        filtered = [
            (token.text, token.lemma_)
            for token in doc
            if not token.is_stop and token.text.strip()
        ]

        original_words = [t[0] for t in filtered]
        lemma_words = [t[1] for t in filtered]

        tokens = self.make_ngrams(original_words) + self.make_ngrams(lemma_words)

        return list(dict.fromkeys(tokens))

    def make_ngrams(self, words: list) -> list:
        # This function generates all forward-combination n-grams (not just adjacent ones)
        # It builds:
        # - 1-grams: single words
        # - 2-grams: all pairs where i < j
        # - 3-grams: all triplets where i < j < k

        ngrams = []

        # -------------------------
        # 1-grams (unigrams)
        # -------------------------
        # Each word is kept as-is
        # ngrams.extend(words)

        # -------------------------
        # 2-grams (bigrams)
        # -------------------------
        # Create all combinations of two words where the second word comes after the first
        # Example: [a, b, c] → a-b, a-c, b-c
        for i in range(len(words)):
            for j in range(i + 1, len(words)):
                ngrams.append(f"{words[i]}-{words[j]}")

        # -------------------------
        # 3-grams (trigrams)
        # -------------------------
        # Create all combinations of three words in forward order (i < j < k)
        # Example: [a, b, c, d] → a-b-c, a-b-d, a-c-d, b-c-d
        for i in range(len(words)):
            for j in range(i + 1, len(words)):
                for k in range(j + 1, len(words)):
                    ngrams.append(f"{words[i]}-{words[j]}-{words[k]}")

        return ngrams

    def get_canonical_tags(self, query_tags: list) -> list:
        tags: QuerySet[TagAlias] = (
            TagAlias.objects
            .filter(raw_tag__in=list(query_tags))
            .filter(canonical_tag__isnull=False)
            .values_list('canonical_tag__slug', flat=True)
        )

        if tags:
            return list(tags)

        return []
