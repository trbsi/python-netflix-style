import re

import spacy
from django.core import signing
from spacy.cli import download

from src.discovery.models import TagAlias


class PersonalizeSiteService():
    def personalize_site(self, text: str) -> str | None:
        text = self.clean_query(text)
        text_array = self.to_tokens(text)
        tags = self.get_canonical_tags(text_array)

        if not tags:
            return None

        signed_value = signing.dumps({
            "tags": ','.join(tags),
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

        def make_ngrams(words):
            ngrams = []
            for n in (1, 2, 3):
                for i in range(len(words) - n + 1):
                    ngrams.append('-'.join(words[i:i + n]))
            return ngrams

        tokens = make_ngrams(original_words) + make_ngrams(lemma_words)

        return list(dict.fromkeys(tokens))

    def get_canonical_tags(self, tags: list) -> list | None:
        tags = (
            TagAlias.objects
            .filter(raw_tag__in=tags)
            .filter(canonical_tag__isnull=False)
            .values_list('canonical_tag__slug', flat=True)
        )
        if tags:
            tags = list(set(tags))
            return tags

        return None
